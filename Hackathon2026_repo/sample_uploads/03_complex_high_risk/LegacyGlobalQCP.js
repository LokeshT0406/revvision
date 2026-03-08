export function onInit(quote, lines, conn) {
  return conn.query("SELECT Id, SBQQ__NetPrice__c FROM SBQQ__QuoteLine__c WHERE SBQQ__Quote__c = 'a1B5g00000ABCdE'");
}

export function onBeforeCalculate(quote, lines, conn) {
  if (quote.record.SBQQ__Status__c === 'Draft') {
    return conn.query("SELECT Id FROM SBQQ__QuoteLine__c WHERE SBQQ__Quote__c = 'a1B5g00000ABCdE'");
  }
  return Promise.resolve();
}

export function onCalculate(quote, lines, conn) {
  if (lines.length > 50) {
    quote.record.SBQQ__AdditionalDiscountAmount__c = 500;
  }
  return Promise.resolve();
}

export function onAfterCalculate(quote, lines, conn) {
  return Promise.resolve();
}

export function onAfterFinalCalc(quote, lines, conn) {
  return Promise.resolve();
}
