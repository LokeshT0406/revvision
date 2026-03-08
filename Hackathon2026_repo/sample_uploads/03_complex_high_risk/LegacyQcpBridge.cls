public with sharing class LegacyQcpBridge {
    public static void run(Id quoteId) {
        String dynamicSoql = 'SELECT Id, SBQQ__NetPrice__c FROM SBQQ__QuoteLine__c WHERE SBQQ__Quote__c = \'a1B5g00000ABCdE\'';
        List<SBQQ__QuoteLine__c> lines = Database.query(dynamicSoql);
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:LegacyPricingService');
        req.setMethod('POST');
        req.setBody('quote=' + quoteId);
        Http http = new Http();
        HttpResponse res = http.send(req);
        System.debug(res.getStatusCode());
    }

    public static void onBeforeCalculate() {
        System.debug('Hook simulation');
    }

    public static void onCalculate() {
        System.debug('Hook simulation');
    }

    public static void onAfterCalculate() {
        System.debug('Hook simulation');
    }
}
