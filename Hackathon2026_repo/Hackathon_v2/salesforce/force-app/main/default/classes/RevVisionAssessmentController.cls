public with sharing class RevVisionAssessmentController {
    public class ArtifactInput {
        @AuraEnabled public String fileName;
        @AuraEnabled public String content;
    }

    public class ArtifactResult {
        @AuraEnabled public String fileName;
        @AuraEnabled public String typeKey;
        @AuraEnabled public Integer score;
        @AuraEnabled public String risk;
        @AuraEnabled public Decimal estWeeks;
        @AuraEnabled public Integer conditions;
        @AuraEnabled public Integer actions;
        @AuraEnabled public Integer lookups;
        @AuraEnabled public Integer soqlHits;
        @AuraEnabled public Integer hardcodedIds;
        @AuraEnabled public Integer sbqqRefs;
        @AuraEnabled public Integer qcpHooks;
    }

    public class AssessmentResult {
        @AuraEnabled public Integer totalFiles;
        @AuraEnabled public Integer totalScore;
        @AuraEnabled public String orgRisk;
        @AuraEnabled public Decimal totalEstWeeks;
        @AuraEnabled public Integer inputRows;
        @AuraEnabled public String readinessStatus;
        @AuraEnabled public Integer confidenceScore;
        @AuraEnabled public String confidenceLabel;
        @AuraEnabled public Integer mandatoryMet;
        @AuraEnabled public Integer mandatoryTotal;
        @AuraEnabled public Integer highCriticalFiles;
        @AuraEnabled public Integer pricingConditions;
        @AuraEnabled public Integer pricingActions;
        @AuraEnabled public Integer pricingLookups;
        @AuraEnabled public Integer pricingQcpFiles;
        @AuraEnabled public Integer highRiskPricingFiles;
        @AuraEnabled public List<ArtifactResult> artifacts;
        @AuraEnabled public List<RiskRangeRow> riskRanges;
        @AuraEnabled public List<CoverageRow> coverageRows;
        @AuraEnabled public List<String> roadmap;
        @AuraEnabled public List<String> mappingBullets;
        @AuraEnabled public String blueprintText;
    }

    public class RiskRangeRow {
        @AuraEnabled public String risk;
        @AuraEnabled public String rangeLabel;
    }

    public class CoverageRow {
        @AuraEnabled public String component;
        @AuraEnabled public String status;
        @AuraEnabled public Integer artifacts;
    }

    private class ScoreBreakdown {
        public Integer score;
        public Integer conditions;
        public Integer actions;
        public Integer lookups;
        public Integer soqlHits;
        public Integer hardcodedIds;
        public Integer sbqqRefs;
        public Integer qcpHooks;
    }

    @AuraEnabled(cacheable=false)
    public static AssessmentResult analyzeArtifacts(
        List<Object> artifacts,
        Integer lowThreshold,
        Integer moderateThreshold,
        Integer highThreshold
    ) {
        Integer low = lowThreshold == null ? 250 : lowThreshold;
        Integer moderate = moderateThreshold == null ? 500 : moderateThreshold;
        Integer high = highThreshold == null ? 750 : highThreshold;

        AssessmentResult output = new AssessmentResult();
        output.artifacts = new List<ArtifactResult>();
        output.roadmap = new List<String>();
        output.riskRanges = buildRiskRanges(low, moderate, high);
        output.coverageRows = new List<CoverageRow>();
        output.inputRows = artifacts == null ? 0 : artifacts.size();
        output.mandatoryTotal = 4;

        if (artifacts == null || artifacts.isEmpty()) {
            output.totalFiles = 0;
            output.totalScore = 0;
            output.totalEstWeeks = 0;
            output.orgRisk = 'LOW';
            output.readinessStatus = 'INCOMPLETE';
            output.confidenceScore = 0;
            output.confidenceLabel = 'LOW';
            output.mandatoryMet = 0;
            output.highCriticalFiles = 0;
            output.pricingConditions = 0;
            output.pricingActions = 0;
            output.pricingLookups = 0;
            output.pricingQcpFiles = 0;
            output.highRiskPricingFiles = 0;
            output.coverageRows = buildCoverageRows(output.artifacts);
            output.mappingBullets = new List<String>();
            output.blueprintText = 'No artifacts uploaded.';
            return output;
        }

        Integer totalScore = 0;
        Decimal totalWeeks = 0;
        Set<String> typeKeys = new Set<String>();
        Integer conditionsTotal = 0;
        Integer actionsTotal = 0;
        Integer lookupsTotal = 0;
        Integer qcpFiles = 0;
        Integer highCritical = 0;
        Integer highRiskPricing = 0;
        Integer unknownFiles = 0;
        Integer supportedFiles = 0;

        List<ArtifactInput> normalized = (List<ArtifactInput>) JSON.deserialize(
            JSON.serialize(artifacts),
            List<ArtifactInput>.class
        );

        for (ArtifactInput input : normalized) {
            if (input == null) continue;
            String fileName = input.fileName;
            String content = input.content;

            if (String.isBlank(fileName)) {
                continue;
            }

            String raw = String.isBlank(content) ? '' : content;
            String typeKey = detectType(fileName, raw);
            ScoreBreakdown breakdown = computeScoreBreakdown(typeKey, raw);
            Integer score = breakdown.score;
            String risk = getRisk(score, low, moderate, high);
            Decimal weeks = computeWeeks(score);

            ArtifactResult item = new ArtifactResult();
            item.fileName = fileName;
            item.typeKey = typeKey;
            item.score = score;
            item.risk = risk;
            item.estWeeks = weeks;
            item.conditions = breakdown.conditions;
            item.actions = breakdown.actions;
            item.lookups = breakdown.lookups;
            item.soqlHits = breakdown.soqlHits;
            item.hardcodedIds = breakdown.hardcodedIds;
            item.sbqqRefs = breakdown.sbqqRefs;
            item.qcpHooks = breakdown.qcpHooks;
            output.artifacts.add(item);

            totalScore += score;
            totalWeeks += weeks;
            typeKeys.add(typeKey);
            conditionsTotal += breakdown.conditions;
            actionsTotal += breakdown.actions;
            lookupsTotal += breakdown.lookups;
            if (typeKey == 'qcp') qcpFiles++;
            if (risk == 'HIGH' || risk == 'CRITICAL') highCritical++;
            if (typeKey == 'price_rule' || typeKey == 'product_rule' || typeKey == 'qcp') {
                if (risk == 'HIGH' || risk == 'CRITICAL') highRiskPricing++;
            }
            if (typeKey == 'unknown') unknownFiles++;
            else supportedFiles++;
        }

        output.coverageRows = buildCoverageRows(output.artifacts);
        Integer missingMandatory = 0;
        Integer mandatoryMet = 0;
        for (CoverageRow row : output.coverageRows) {
            if (row.status == 'OK') mandatoryMet++;
            else missingMandatory++;
        }

        Integer confidence = 100;
        if (supportedFiles < 6) confidence -= 30;
        confidence -= Math.min(20, unknownFiles * 8);
        confidence -= missingMandatory * 18;
        if ((countByTypes(output.artifacts, new Set<String>{'price_rule', 'product_rule', 'qcp'})) < 2) confidence -= 20;
        if (confidence < 0) confidence = 0;

        output.totalFiles = output.artifacts.size();
        output.totalScore = totalScore;
        output.totalEstWeeks = totalWeeks.setScale(1);
        output.orgRisk = getRisk(totalScore, low, moderate, high);
        output.readinessStatus = (missingMandatory == 0 && confidence >= 75) ? 'READY' : (mandatoryMet > 0 ? 'PARTIAL' : 'INCOMPLETE');
        output.confidenceScore = confidence;
        output.confidenceLabel = confidence >= 75 ? 'HIGH' : (confidence >= 45 ? 'MEDIUM' : 'LOW');
        output.mandatoryMet = mandatoryMet;
        output.highCriticalFiles = highCritical;
        output.pricingConditions = conditionsTotal;
        output.pricingActions = actionsTotal;
        output.pricingLookups = lookupsTotal;
        output.pricingQcpFiles = qcpFiles;
        output.highRiskPricingFiles = highRiskPricing;
        output.roadmap = buildRoadmap(output.artifacts);
        output.mappingBullets = buildMappings(typeKeys);
        output.blueprintText = buildDetailedBlueprint(output.artifacts, output.mappingBullets);
        return output;
    }

    private static String detectType(String fileName, String content) {
        String name = fileName == null ? '' : fileName.toLowerCase();
        String body = content == null ? '' : content.toLowerCase();

        if (name.endsWith('.trigger')) return 'apex_trigger';
        if (name.endsWith('.cls') || name.endsWith('.apex')) return 'apex_class';
        if (name.endsWith('.flow') || name.endsWith('.flow-meta.xml')) return 'flow';
        if (name.endsWith('.js') || name.endsWith('.resource')) return 'qcp';
        if (name.endsWith('.object-meta.xml')) return 'object_metadata';

        if (name.endsWith('.xml')) {
            if (body.contains('pricingrule') || body.contains('priceactions')) return 'price_rule';
            if (body.contains('productrule') || body.contains('errorconditionmet')) return 'product_rule';
            if (body.contains('lookuptable')) return 'lookup_table';
            if (body.contains('summaryvariable')) return 'summary_variable';
            return 'xml_generic';
        }

        return 'unknown';
    }

    private static ScoreBreakdown computeScoreBreakdown(String typeKey, String content) {
        Integer base = 10;
        Map<String, Integer> baseWeights = new Map<String, Integer>{
            'qcp' => 95,
            'apex_trigger' => 75,
            'apex_class' => 62,
            'flow' => 52,
            'product_rule' => 45,
            'price_rule' => 40,
            'lookup_table' => 24,
            'summary_variable' => 20,
            'object_metadata' => 16,
            'xml_generic' => 14,
            'unknown' => 10
        };

        if (baseWeights.containsKey(typeKey)) {
            base = baseWeights.get(typeKey);
        }

        String body = content == null ? '' : content;
        Integer conditions = countMatches(body, '(?i)\\bif\\s*\\(');
        Integer actions = countMatches(body, '(?i)\\b(update|insert|upsert|delete|set\\s+)\\b');
        Integer lookups = countMatches(body, '(?i)\\blookup\\b|lookupTable');
        Integer soqlCount = countMatches(body, '(?i)\\bselect\\b');
        Integer idCount = countMatches(body, '00[A-Za-z0-9]{12,15}');
        Integer sbqqRefs = countMatches(body, '(?i)SBQQ__');
        Integer hookCount = countMatches(body, '(?i)onBeforeCalculate|onCalculate|onAfterCalculate|onInit|onAfterFinalCalc');

        Integer raw = base
            + (conditions * 2)
            + (actions * 4)
            + (lookups * 5)
            + (soqlCount * 8)
            + (idCount * 18)
            + (sbqqRefs * 6)
            + (hookCount * 22);

        if (typeKey == 'qcp') raw += 45;
        if (typeKey == 'apex_trigger') raw += 12;

        ScoreBreakdown out = new ScoreBreakdown();
        out.score = Math.min(1000, Math.max(0, raw));
        out.conditions = conditions;
        out.actions = actions;
        out.lookups = lookups;
        out.soqlHits = soqlCount;
        out.hardcodedIds = idCount;
        out.sbqqRefs = sbqqRefs;
        out.qcpHooks = hookCount;
        return out;
    }

    private static String getRisk(Integer score, Integer low, Integer moderate, Integer high) {
        if (score < low) return 'LOW';
        if (score < moderate) return 'MODERATE';
        if (score < high) return 'HIGH';
        return 'CRITICAL';
    }

    private static Decimal computeWeeks(Integer score) {
        Decimal v = (Decimal.valueOf(score) / Decimal.valueOf(1000)) * Decimal.valueOf(2);
        if (v < 0.1) v = 0.1;
        return v.setScale(1);
    }

    private static List<RiskRangeRow> buildRiskRanges(Integer low, Integer moderate, Integer high) {
        List<RiskRangeRow> rows = new List<RiskRangeRow>();

        RiskRangeRow r1 = new RiskRangeRow();
        r1.risk = 'LOW';
        r1.rangeLabel = '0 to ' + String.valueOf(low - 1);
        rows.add(r1);

        RiskRangeRow r2 = new RiskRangeRow();
        r2.risk = 'MODERATE';
        r2.rangeLabel = String.valueOf(low) + ' to ' + String.valueOf(moderate - 1);
        rows.add(r2);

        RiskRangeRow r3 = new RiskRangeRow();
        r3.risk = 'HIGH';
        r3.rangeLabel = String.valueOf(moderate) + ' to ' + String.valueOf(high - 1);
        rows.add(r3);

        RiskRangeRow r4 = new RiskRangeRow();
        r4.risk = 'CRITICAL';
        r4.rangeLabel = String.valueOf(high) + ' to 1000';
        rows.add(r4);

        return rows;
    }

    private static Integer countByTypes(List<ArtifactResult> artifacts, Set<String> wanted) {
        Integer count = 0;
        for (ArtifactResult a : artifacts) {
            if (a != null && wanted.contains(a.typeKey)) {
                count++;
            }
        }
        return count;
    }

    private static List<CoverageRow> buildCoverageRows(List<ArtifactResult> artifacts) {
        List<CoverageRow> rows = new List<CoverageRow>();

        Integer pricingLogic = countByTypes(artifacts, new Set<String>{'price_rule', 'product_rule', 'qcp'});
        Integer automation = countByTypes(artifacts, new Set<String>{'flow', 'apex_class', 'apex_trigger'});
        Integer pricingData = countByTypes(artifacts, new Set<String>{'lookup_table', 'summary_variable', 'price_rule'});
        Integer customization = countByTypes(artifacts, new Set<String>{'object_metadata', 'apex_class', 'apex_trigger'});

        rows.add(buildCoverageRow('Pricing logic (Price Rule / Product Rule / QCP)', pricingLogic));
        rows.add(buildCoverageRow('Quote automation (Flow / Apex)', automation));
        rows.add(buildCoverageRow('Pricing data inputs (Lookup / Summary / Price Rule)', pricingData));
        rows.add(buildCoverageRow('Org customization layer (Object metadata or Apex)', customization));

        return rows;
    }

    private static CoverageRow buildCoverageRow(String label, Integer count) {
        CoverageRow row = new CoverageRow();
        row.component = label;
        row.artifacts = count;
        row.status = count > 0 ? 'OK' : 'MISSING';
        return row;
    }

    private static Integer countMatches(String input, String regex) {
        if (String.isBlank(input)) return 0;
        Pattern p = Pattern.compile(regex);
        Matcher m = p.matcher(input);
        Integer count = 0;
        while (m.find()) count++;
        return count;
    }

    private static List<String> buildRoadmap(List<ArtifactResult> artifacts) {
        Integer lowMod = 0;
        Integer high = 0;
        Integer critical = 0;

        for (ArtifactResult a : artifacts) {
            if (a.risk == 'LOW' || a.risk == 'MODERATE') lowMod++;
            else if (a.risk == 'HIGH') high++;
            else if (a.risk == 'CRITICAL') critical++;
        }

        List<String> steps = new List<String>();
        if (lowMod > 0) steps.add('Phase 1 - Quick wins (' + lowMod + ' artifacts)');
        if (high > 0) steps.add('Phase 2 - Core migration (' + high + ' artifacts)');
        if (critical > 0) steps.add('Phase 3 - Architect-led complex assets (' + critical + ' artifacts)');
        return steps;
    }

    private static List<String> buildMappings(Set<String> typeKeys) {
        Set<String> needed = new Set<String>();

        if (typeKeys.contains('qcp') || typeKeys.contains('apex_class') || typeKeys.contains('apex_trigger') || typeKeys.contains('flow')) {
            needed.add('SBQQ__Quote__c');
            needed.add('SBQQ__QuoteLine__c');
        }
        if (typeKeys.contains('qcp') || typeKeys.contains('apex_class')) {
            needed.add('SBQQ__Subscription__c');
        }
        if (typeKeys.contains('product_rule') || typeKeys.contains('apex_class')) {
            needed.add('SBQQ__ProductOption__c');
        }
        if (typeKeys.contains('price_rule') || typeKeys.contains('apex_class')) {
            needed.add('SBQQ__PriceRule__c');
        }

        Map<String, String> mapping = new Map<String, String>{
            'SBQQ__Quote__c' => 'SalesTransaction',
            'SBQQ__QuoteLine__c' => 'SalesTransactionItem',
            'SBQQ__Subscription__c' => 'Asset',
            'SBQQ__ProductOption__c' => 'ProductComponent',
            'SBQQ__PriceRule__c' => 'Pricing Procedure Step'
        };

        List<String> bullets = new List<String>();
        for (String key : mapping.keySet()) {
            if (needed.contains(key)) {
                bullets.add(key + ' -> ' + mapping.get(key));
            }
        }
        bullets.sort();
        return bullets;
    }

    private static String buildDetailedBlueprint(List<ArtifactResult> artifacts, List<String> mappingBullets) {
        if (artifacts == null || artifacts.isEmpty()) {
            return 'No artifacts to build blueprint.';
        }

        List<ArtifactResult> sorted = new List<ArtifactResult>();
        sorted.addAll(artifacts);
        sorted.sort(new ArtifactScoreDescComparator());

        List<String> lines = new List<String>();
        lines.add('# CPQ to RCA Migration Blueprint (Portfolio)');
        lines.add('');
        lines.add('## In-Scope Object Mapping');
        if (mappingBullets != null && !mappingBullets.isEmpty()) {
            for (String mappingLine : mappingBullets) {
                lines.add('- ' + mappingLine);
            }
        } else {
            lines.add('- No direct SBQQ to RCA mappings detected for this upload set.');
        }
        lines.add('');
        lines.add('## Artifact Blueprints');
        lines.add('');

        Integer maxItems = sorted.size();
        for (Integer i = 0; i < maxItems; i++) {
            ArtifactResult a = sorted[i];
            lines.add('### ' + (i + 1) + '. ' + a.fileName);
            lines.add('- Type: ' + a.typeKey);
            lines.add('- Risk: ' + a.risk);
            lines.add('- Score: ' + String.valueOf(a.score));
            lines.add('- Estimated effort: ' + String.valueOf(a.estWeeks) + ' weeks');
            lines.add('');
            lines.add('Migration actions:');
            for (String note : migrationNotesForType(a.typeKey, a.risk)) {
                lines.add('- ' + note);
            }
            lines.add('');
            lines.add('Validation checks:');
            lines.add('- Compare CPQ and RCA pricing output for baseline quote scenarios.');
            lines.add('- Validate amendment and renewal parity for affected products.');
            lines.add('- Confirm no hardcoded IDs or unsupported QCP runtime dependencies remain.');
            lines.add('');
        }
        lines.add('## Recommended Execution Order');
        lines.add('- Phase 1: LOW/MODERATE artifacts');
        lines.add('- Phase 2: HIGH artifacts');
        lines.add('- Phase 3: CRITICAL artifacts');
        return String.join(lines, '\n');
    }

    private static List<String> migrationNotesForType(String typeKey, String risk) {
        List<String> notes = new List<String>();
        if (typeKey == 'qcp') {
            notes.add('Rebuild QCP hooks as RCA pricing procedure steps and Apex actions.');
            notes.add('Move JavaScript pricing logic into Apex services for maintainability.');
        } else if (typeKey == 'apex_class' || typeKey == 'apex_trigger') {
            notes.add('Replace SBQQ object references with RCA object equivalents.');
            notes.add('Refactor SOQL-heavy logic into service methods and add unit tests.');
        } else if (typeKey == 'price_rule' || typeKey == 'product_rule') {
            notes.add('Translate rule conditions/actions into RCA decision tables and procedure steps.');
            notes.add('Preserve rule execution order and dependency behavior.');
        } else if (typeKey == 'flow') {
            notes.add('Review flow nodes and replace CPQ-specific invocables with RCA-compatible actions.');
            notes.add('Retest quote lifecycle transitions in target org.');
        } else if (typeKey == 'lookup_table' || typeKey == 'summary_variable') {
            notes.add('Map lookup/summary logic into RCA pricing matrices or equivalent metadata.');
            notes.add('Validate reference data completeness in migration package.');
        } else if (typeKey == 'object_metadata') {
            notes.add('Review custom fields/metadata and map to RCA object model extensions.');
            notes.add('Update layouts/FLS and dependent automation after migration.');
        } else {
            notes.add('Manually review this artifact and map any SBQQ dependencies to RCA.');
        }

        if (risk == 'HIGH' || risk == 'CRITICAL') {
            notes.add('Requires architect review before implementation.');
        }
        return notes;
    }

    public class ArtifactScoreDescComparator implements Comparator<ArtifactResult> {
        public Integer compare(ArtifactResult a, ArtifactResult b) {
            Integer ascore = a == null || a.score == null ? 0 : a.score;
            Integer bscore = b == null || b.score == null ? 0 : b.score;
            if (ascore == bscore) return 0;
            return ascore > bscore ? -1 : 1;
        }
    }
}
