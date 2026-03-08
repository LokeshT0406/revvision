public with sharing class QuoteMigrationHelper {
    public static void syncQuote(Id quoteId) {
        SBQQ__Quote__c quoteRec = [SELECT Id, Name FROM SBQQ__Quote__c WHERE Id = :quoteId LIMIT 1];
        if (quoteRec != null) {
            update quoteRec;
        }
    }

    public static Decimal calculateTierDiscount(Decimal amount) {
        if (amount > 50000) return 0.20;
        if (amount > 25000) return 0.12;
        return 0.05;
    }
}
