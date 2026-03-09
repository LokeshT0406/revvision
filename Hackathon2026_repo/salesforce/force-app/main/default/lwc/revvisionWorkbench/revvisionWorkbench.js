import { LightningElement, track } from 'lwc';
import analyzeArtifacts from '@salesforce/apex/RevVisionAssessmentController.analyzeArtifacts';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

const RISK_PRESETS = {
    Balanced: { low: 250, moderate: 500, high: 750 },
    Strict: { low: 150, moderate: 350, high: 600 }
};

const TYPE_LABELS = {
    qcp: 'QCP Script',
    apex_trigger: 'Apex Trigger',
    apex_class: 'Apex Class',
    flow: 'Flow',
    product_rule: 'Product Rule',
    price_rule: 'Price Rule',
    lookup_table: 'Lookup Table',
    summary_variable: 'Summary Variable',
    object_metadata: 'Object Metadata',
    xml_generic: 'XML Generic',
    unknown: 'Unknown'
};

export default class RevvisionWorkbench extends LightningElement {
    @track riskProfile = 'Balanced';
    @track lowThreshold = 250;
    @track moderateThreshold = 500;
    @track highThreshold = 750;
    @track files = [];
    @track result;
    @track selectedFileNames = [];
    @track fileStatus = 'No files selected.';
    @track selectedArtifactName;
    @track blueprintMode = 'portfolio';
    @track blueprintArtifactName;

    columns = [
        { label: 'File', fieldName: 'fileName' },
        { label: 'Type', fieldName: 'typeLabel' },
        { label: 'Score', fieldName: 'score', type: 'number' },
        { label: 'Risk', fieldName: 'risk' },
        { label: 'Est. Weeks', fieldName: 'estWeeks', type: 'number' }
    ];

    parameterColumns = [
        { label: 'File', fieldName: 'fileName' },
        { label: 'Conditions', fieldName: 'conditions', type: 'number' },
        { label: 'Actions', fieldName: 'actions', type: 'number' },
        { label: 'Lookups', fieldName: 'lookups', type: 'number' },
        { label: 'SOQL Hits', fieldName: 'soqlHits', type: 'number' },
        { label: 'Hardcoded IDs', fieldName: 'hardcodedIds', type: 'number' },
        { label: 'SBQQ Refs', fieldName: 'sbqqRefs', type: 'number' },
        { label: 'QCP Hooks', fieldName: 'qcpHooks', type: 'number' }
    ];

    riskRangeColumns = [
        { label: 'Risk', fieldName: 'risk' },
        { label: 'Per-file score range', fieldName: 'rangeLabel' }
    ];

    scoreColumns = [
        { label: 'File', fieldName: 'fileName' },
        { label: 'Score', fieldName: 'score', type: 'number' },
        { label: 'Risk', fieldName: 'risk' }
    ];

    coverageColumns = [
        { label: 'Component', fieldName: 'component' },
        { label: 'Status', fieldName: 'status' },
        { label: 'Artifacts', fieldName: 'artifacts', type: 'number' }
    ];

    artifactSummaryColumns = [
        { label: 'File', fieldName: 'fileName' },
        { label: 'Type', fieldName: 'typeLabel' },
        { label: 'Risk', fieldName: 'risk' },
        { label: 'Score', fieldName: 'score', type: 'number' },
        { label: 'Est. Weeks', fieldName: 'estWeeks', type: 'number' },
        { label: 'Hardcoded IDs', fieldName: 'hardcodedIds', type: 'number' },
        { label: 'SOQL Hits', fieldName: 'soqlHits', type: 'number' }
    ];

    riskDistributionColumns = [
        { label: 'Risk', fieldName: 'risk' },
        { label: 'Count', fieldName: 'count', type: 'number' }
    ];

    typeBreakdownColumns = [
        { label: 'Artifact Type', fieldName: 'typeLabel' },
        { label: 'Count', fieldName: 'count', type: 'number' }
    ];

    get riskProfileOptions() {
        return [
            { label: 'Balanced', value: 'Balanced' },
            { label: 'Strict', value: 'Strict' },
            { label: 'Custom', value: 'Custom' }
        ];
    }

    get blueprintModeOptions() {
        return [
            { label: 'Portfolio (all artifacts)', value: 'portfolio' },
            { label: 'Single artifact', value: 'single' }
        ];
    }

    get isCustomProfile() {
        return this.riskProfile === 'Custom';
    }

    get analyzeDisabled() {
        return this.files.length === 0;
    }

    get selectedFileCount() {
        return this.files.length;
    }

    get hasSelectedFiles() {
        return this.selectedFileNames && this.selectedFileNames.length > 0;
    }

    get artifacts() {
        const rows = this.result?.artifacts || [];
        return rows.map((row) => ({ ...row, typeLabel: this.typeLabel(row.typeKey) }));
    }

    get artifactOptions() {
        return this.artifacts.map((a) => ({ label: a.fileName, value: a.fileName }));
    }

    get hasArtifacts() {
        return this.artifacts.length > 0;
    }

    get selectedArtifact() {
        if (!this.hasArtifacts) {
            return null;
        }
        const requested = this.selectedArtifactName || this.artifacts[0].fileName;
        return this.artifacts.find((a) => a.fileName === requested) || this.artifacts[0];
    }

    get selectedArtifactActions() {
        const row = this.selectedArtifact;
        if (!row) {
            return [];
        }
        return this.actionItemsFor(row);
    }

    get totalConditions() {
        return this.sumField('conditions');
    }

    get totalActions() {
        return this.sumField('actions');
    }

    get totalLookups() {
        return this.sumField('lookups');
    }

    get totalSoqlHits() {
        return this.sumField('soqlHits');
    }

    get totalHardcodedIds() {
        return this.sumField('hardcodedIds');
    }

    get totalQcpHooks() {
        return this.sumField('qcpHooks');
    }

    get readinessStatusText() {
        const status = this.result?.readinessStatus || 'INCOMPLETE';
        if (status === 'READY') return 'Ready to Start';
        if (status === 'PARTIAL') return 'Partially Ready';
        return 'Needs More Input';
    }

    get highCriticalSummary() {
        const hc = this.result?.highCriticalFiles || 0;
        const total = this.result?.totalFiles || 0;
        return `${hc}/${total} files`;
    }

    get qcpFileCount() {
        return this.artifacts.filter((a) => a.typeKey === 'qcp').length;
    }

    get estimatedEffortWeeks() {
        return this.artifacts.reduce((acc, row) => acc + (Number(row.estWeeks) || 0), 0).toFixed(1);
    }

    get roi() {
        const artifacts = this.artifacts.length;
        const manualHours = artifacts * 1.5;
        const aiHours = artifacts * 0.1;
        const hoursSaved = manualHours - aiHours;
        const costSaved = hoursSaved * 75;
        const efficiencyGainPct = manualHours ? Math.round((hoursSaved / manualHours) * 100) : 0;

        return {
            artifacts,
            manualHours: manualHours.toFixed(1),
            aiHours: aiHours.toFixed(1),
            hoursSaved: hoursSaved.toFixed(1),
            costSaved: Math.round(costSaved),
            efficiencyGainPct
        };
    }

    get scoreColumnsRows() {
        return this.artifacts
            .slice()
            .sort((a, b) => (b.score || 0) - (a.score || 0));
    }

    get riskScoreNote() {
        return 'Per-file risk score is calculated from file type weight, conditions, actions, lookups, SOQL hits, hardcoded IDs, SBQQ references, and QCP hooks. Score is capped at 1000 per file.';
    }

    get riskDistributionRows() {
        const counts = { CRITICAL: 0, HIGH: 0, MODERATE: 0, LOW: 0 };
        this.artifacts.forEach((row) => {
            const key = String(row.risk || 'LOW').toUpperCase();
            if (counts[key] !== undefined) counts[key] += 1;
        });
        return Object.keys(counts).map((risk) => ({ risk, count: counts[risk] }));
    }

    get typeBreakdownRows() {
        const map = {};
        this.artifacts.forEach((row) => {
            const typeLabel = this.typeLabel(row.typeKey);
            map[typeLabel] = (map[typeLabel] || 0) + 1;
        });
        return Object.keys(map)
            .sort()
            .map((typeLabel) => ({ typeLabel, count: map[typeLabel] }));
    }

    get roadmapRows() {
        const phase1 = this.artifacts.filter((a) => a.risk === 'LOW' || a.risk === 'MODERATE');
        const phase2 = this.artifacts.filter((a) => a.risk === 'HIGH');
        const phase3 = this.artifacts.filter((a) => a.risk === 'CRITICAL');

        const rows = [];
        if (phase1.length) {
            rows.push(this.buildRoadmapPhaseRow(1, 'Quick Wins', phase1, 'Start with low/moderate complexity artifacts.'));
        }
        if (phase2.length) {
            rows.push(this.buildRoadmapPhaseRow(2, 'Core Migration', phase2, 'Migrate high-risk core business logic.'));
        }
        if (phase3.length) {
            rows.push(this.buildRoadmapPhaseRow(3, 'Complex Assets', phase3, 'Architect-led execution for critical customizations.'));
        }
        return rows;
    }

    get roadmapColumns() {
        return [
            { label: 'Phase', fieldName: 'phase' },
            { label: 'Title', fieldName: 'title' },
            { label: 'Artifacts', fieldName: 'count', type: 'number' },
            { label: 'Est. Weeks', fieldName: 'weeks', type: 'number' },
            { label: 'Description', fieldName: 'description' }
        ];
    }

    get isSingleBlueprintMode() {
        return this.blueprintMode === 'single';
    }

    get selectedBlueprintArtifact() {
        const rows = this.artifacts;
        if (!rows.length) {
            return null;
        }
        const requested = this.blueprintArtifactName || rows[0].fileName;
        return rows.find((a) => a.fileName === requested) || rows[0];
    }

    get blueprintHtml() {
        if (!this.result) {
            return '';
        }

        if (this.isSingleBlueprintMode) {
            const row = this.selectedBlueprintArtifact;
            if (!row) {
                return '';
            }
            const single = this.buildSingleBlueprintText(row);
            return this.toBlueprintHtml(single);
        }

        if (this.result.blueprintText) {
            return this.toBlueprintHtml(this.result.blueprintText);
        }
        return '';
    }

    get mappingBullets() {
        return this.result?.mappingBullets || [];
    }

    get artifactSummaryRows() {
        return this.artifacts
            .slice()
            .sort((a, b) => (b.score || 0) - (a.score || 0));
    }

    openFilePicker() {
        const input = this.template.querySelector('input[data-id="cpqFileInput"]');
        if (input) {
            input.click();
        } else {
            this.fileStatus = 'File picker not available. Refresh page and try again.';
        }
    }

    handleRiskProfileChange(event) {
        this.riskProfile = event.detail.value;
        if (this.riskProfile !== 'Custom') {
            const preset = RISK_PRESETS[this.riskProfile];
            this.lowThreshold = preset.low;
            this.moderateThreshold = preset.moderate;
            this.highThreshold = preset.high;
        }
    }

    handleLowChange(event) {
        this.lowThreshold = Number(event.detail.value);
    }

    handleModerateChange(event) {
        this.moderateThreshold = Number(event.detail.value);
    }

    handleHighChange(event) {
        this.highThreshold = Number(event.detail.value);
    }

    handleArtifactChange(event) {
        this.selectedArtifactName = event.detail.value;
    }

    handleBlueprintModeChange(event) {
        this.blueprintMode = event.detail.value;
    }

    handleBlueprintArtifactChange(event) {
        this.blueprintArtifactName = event.detail.value;
    }

    async handleFilesSelected(event) {
        const rawFiles = event?.target?.files || event?.detail?.files || [];
        const selected = Array.from(rawFiles);

        if (!selected.length) {
            this.files = [];
            this.selectedFileNames = [];
            this.fileStatus = 'No files selected.';
            return;
        }

        this.selectedFileNames = selected.map((f) => f.name);
        this.fileStatus = `${selected.length} file(s) selected. Reading content...`;

        try {
            const converted = [];
            for (const file of selected) {
                const content = await this.readFile(file);
                converted.push({ fileName: file.name, content });
            }
            this.files = converted;
            this.fileStatus = `${this.files.length} file(s) ready for analysis.`;
        } catch (e) {
            this.files = [];
            this.selectedFileNames = [];
            this.fileStatus = `File read failed: ${this.reduceError(e)}`;
        }
    }

    readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result || '');
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    async handleAnalyze() {
        if (this.lowThreshold >= this.moderateThreshold || this.moderateThreshold >= this.highThreshold) {
            this.notify('Invalid thresholds', 'Low < Moderate < High is required.', 'error');
            return;
        }

        try {
            this.result = await analyzeArtifacts({
                artifacts: this.files,
                lowThreshold: this.lowThreshold,
                moderateThreshold: this.moderateThreshold,
                highThreshold: this.highThreshold
            });
            if (this.result && this.result.blueprintText) {
                this.result = {
                    ...this.result,
                    blueprintText: this.result.blueprintText.replace(/\\n/g, '\n')
                };
            }
            this.selectedArtifactName = this.artifacts.length ? this.artifacts[0].fileName : null;
            this.blueprintArtifactName = this.artifacts.length ? this.artifacts[0].fileName : null;
            this.notify('Assessment complete', `Analyzed ${this.result.totalFiles} artifacts.`, 'success');
        } catch (e) {
            this.notify('Assessment failed', this.reduceError(e), 'error');
        }
    }

    reduceError(error) {
        if (!error) return 'Unknown error';
        if (error.body && error.body.message) return error.body.message;
        if (error.message) return error.message;
        return JSON.stringify(error);
    }

    notify(title, message, variant) {
        this.dispatchEvent(new ShowToastEvent({ title, message, variant }));
    }

    sumField(fieldName) {
        if (!this.result || !this.result.artifacts) {
            return 0;
        }
        return this.result.artifacts.reduce((acc, row) => acc + (Number(row[fieldName]) || 0), 0);
    }

    typeLabel(typeKey) {
        return TYPE_LABELS[typeKey] || 'Unknown';
    }

    buildRoadmapPhaseRow(phase, title, rows, description) {
        const weeks = rows.reduce((acc, row) => acc + (Number(row.estWeeks) || 0), 0);
        return {
            phase: `Phase ${phase}`,
            title,
            count: rows.length,
            weeks: Number(weeks.toFixed(1)),
            description
        };
    }

    buildSingleBlueprintText(row) {
        const lines = [];
        lines.push(`# Migration Blueprint: ${row.fileName}`);
        lines.push(`Type: ${this.typeLabel(row.typeKey)} | Risk: ${row.risk} | Score: ${row.score}`);
        lines.push('');
        lines.push('## Migration actions');
        this.actionItemsFor(row).forEach((item) => lines.push(`- ${item}`));
        lines.push('');
        lines.push('## Validation checks');
        lines.push('- Compare CPQ and RCA pricing output for baseline quote scenarios.');
        lines.push('- Validate amendment and renewal parity for affected products.');
        lines.push('- Confirm no hardcoded IDs or unsupported QCP runtime dependencies remain.');
        return lines.join('\n');
    }

    actionItemsFor(row) {
        const actions = [];
        if ((row.hardcodedIds || 0) > 0) {
            actions.push('Replace hardcoded Salesforce IDs with metadata/config references.');
        }
        if ((row.soqlHits || 0) > 0) {
            actions.push('Refactor SOQL-heavy logic into service classes.');
        }
        if (row.typeKey === 'qcp' || (row.qcpHooks || 0) > 0) {
            actions.push('Rebuild QCP logic as RCA pricing procedure + Apex actions.');
        }
        if ((row.sbqqRefs || 0) > 0) {
            actions.push('Replace SBQQ references with RCA object model mapping.');
        }
        if (!actions.length) {
            actions.push('No critical action items detected.');
        }
        return actions;
    }

    toBlueprintHtml(text) {
        if (!text) {
            return '';
        }

        const lines = text.split('\n');
        const html = [];
        let inList = false;

        lines.forEach((raw) => {
            const line = (raw || '').trim();
            if (!line) {
                if (inList) {
                    html.push('</ul>');
                    inList = false;
                }
                return;
            }

            if (line.startsWith('#')) {
                if (inList) {
                    html.push('</ul>');
                    inList = false;
                }
                const title = this.escapeHtml(line.replace(/^#+\s*/, ''));
                html.push(`<p><strong>&bull; ${title}</strong></p>`);
                return;
            }

            if (line.startsWith('- ')) {
                if (!inList) {
                    html.push('<ul>');
                    inList = true;
                }
                const item = this.escapeHtml(line.slice(2));
                html.push(`<li>${item}</li>`);
                return;
            }

            if (inList) {
                html.push('</ul>');
                inList = false;
            }
            html.push(`<p>${this.escapeHtml(line)}</p>`);
        });

        if (inList) {
            html.push('</ul>');
        }
        return html.join('');
    }

    escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
}
