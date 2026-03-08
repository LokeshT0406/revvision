import { LightningElement, track } from 'lwc';
import analyzeArtifacts from '@salesforce/apex/RevVisionAssessmentController.analyzeArtifacts';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

const RISK_PRESETS = {
    Balanced: { low: 250, moderate: 500, high: 750 },
    Strict: { low: 150, moderate: 350, high: 600 }
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

    columns = [
        { label: 'File', fieldName: 'fileName' },
        { label: 'Type', fieldName: 'typeKey' },
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

    get riskProfileOptions() {
        return [
            { label: 'Balanced', value: 'Balanced' },
            { label: 'Strict', value: 'Strict' },
            { label: 'Custom', value: 'Custom' }
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

    get riskScoreNote() {
        return `Per-file risk score is calculated from file type weight, conditions, actions, lookups, SOQL hits, hardcoded IDs, SBQQ references, and QCP hooks. Score is capped at 1000 per file.`;
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
                    blueprintText: this.result.blueprintText.replace(/\\\\n/g, '\n')
                };
                this.result.blueprintHtml = this.toBlueprintHtml(this.result.blueprintText);
            }
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
        this.dispatchEvent(
            new ShowToastEvent({ title, message, variant })
        );
    }

    sumField(fieldName) {
        if (!this.result || !this.result.artifacts) {
            return 0;
        }
        return this.result.artifacts.reduce((acc, row) => acc + (Number(row[fieldName]) || 0), 0);
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
