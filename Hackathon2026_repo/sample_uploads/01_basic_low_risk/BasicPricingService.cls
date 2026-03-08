public with sharing class BasicPricingService {
    public static Decimal applyMarkup(Decimal listPrice) {
        Decimal markup = 0.10;
        return listPrice + (listPrice * markup);
    }
}
