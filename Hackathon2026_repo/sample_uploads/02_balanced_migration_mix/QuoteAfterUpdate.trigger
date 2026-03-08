trigger QuoteAfterUpdate on SBQQ__Quote__c (after update) {
    for (SBQQ__Quote__c q : Trigger.new) {
        if (q.Id != null) {
            System.debug('Quote updated: ' + q.Id);
        }
    }
}
