@IsTest
private class RevVisionOpenAiServiceTest {
    private class OpenAiMock implements HttpCalloutMock {
        public HttpResponse respond(HttpRequest req) {
            HttpResponse res = new HttpResponse();
            res.setStatusCode(200);
            res.setBody('{"choices":[{"message":{"content":"mocked response"}}]}');
            return res;
        }
    }

    @IsTest
    static void chat_returnsMessageFromOpenAiResponse() {
        Test.setMock(HttpCalloutMock.class, new OpenAiMock());
        Test.startTest();
        String out = RevVisionOpenAiService.chat('gpt-4o-mini', 'System', 'Hello');
        Test.stopTest();
        System.assertEquals('mocked response', out);
    }
}
