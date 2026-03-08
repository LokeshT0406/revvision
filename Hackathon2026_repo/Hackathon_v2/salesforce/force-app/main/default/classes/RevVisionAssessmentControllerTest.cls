@IsTest
private class RevVisionAssessmentControllerTest {
    @IsTest
    static void analyzeArtifacts_returnsSummaryAndMappings() {
        List<Object> input = new List<Object>{
            new Map<String, Object>{
                'fileName' => 'QuoteLogic.cls',
                'content' => 'public class QuoteLogic { if(true){ System.debug(\'x\'); } }'
            },
            new Map<String, Object>{
                'fileName' => 'QcpHooks.js',
                'content' => 'function onBeforeCalculate(){} function onAfterCalculate(){}'
            }
        };

        Test.startTest();
        RevVisionAssessmentController.AssessmentResult result =
            RevVisionAssessmentController.analyzeArtifacts(input, 180, 280, 420);
        Test.stopTest();

        System.assertEquals(2, result.totalFiles);
        System.assert(result.totalScore > 0);
        System.assertNotEquals(null, result.orgRisk);
        System.assert(result.mappingBullets.size() > 0);
        System.assert(result.roadmap.size() > 0);
    }

    @IsTest
    static void analyzeArtifacts_emptyInput() {
        Test.startTest();
        RevVisionAssessmentController.AssessmentResult result =
            RevVisionAssessmentController.analyzeArtifacts(new List<Object>(), 180, 280, 420);
        Test.stopTest();

        System.assertEquals(0, result.totalFiles);
        System.assertEquals(0, result.totalScore);
        System.assertEquals('LOW', result.orgRisk);
    }
}
