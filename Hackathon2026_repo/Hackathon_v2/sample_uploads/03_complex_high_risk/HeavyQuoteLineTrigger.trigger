trigger HeavyQuoteLineTrigger on SBQQ__QuoteLine__c (before insert, after update) {
    for (SBQQ__QuoteLine__c line : Trigger.new) {
        if (line.SBQQ__Quantity__c > 100) {
            line.Description = 'Large deal';
        }
    }
}
