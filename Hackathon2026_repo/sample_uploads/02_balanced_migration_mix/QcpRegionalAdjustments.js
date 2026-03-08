export function onInit(quote, lines, conn) {
  return Promise.resolve();
}

export function onBeforeCalculate(quote, lines, conn) {
  if (quote.record.SBQQ__Type__c === 'Amendment') {
    return conn.query("SELECT Id FROM SBQQ__QuoteLine__c WHERE SBQQ__Quote__c = 'a1B5g00000ABCdE'");
  }
  return Promise.resolve();
}

export function onAfterCalculate(quote, lines, conn) {
  return Promise.resolve();
}
