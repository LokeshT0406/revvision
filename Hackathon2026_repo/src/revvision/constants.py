from __future__ import annotations

from revvision.types import FileTypeMatch


FILE_TYPE_RULES: dict[str, FileTypeMatch] = {
    "apex_class": FileTypeMatch("apex_class", "Apex Class", "badge-apex", [".cls", ".apex"], ["class ", "public ", "global ", "trigger "]),
    "apex_trigger": FileTypeMatch("apex_trigger", "Apex Trigger", "badge-apex", [".trigger"], ["trigger ", "before insert", "after update"]),
    "flow": FileTypeMatch("flow", "Flow", "badge-flow", [".flow", ".flow-meta.xml"], ["<Flow", "<processType>"]),
    "qcp": FileTypeMatch("qcp", "QCP (JS)", "badge-qcp", [".js", ".resource"], ["onBeforeCalculate", "onCalculate", "SBQQ"]),
    "price_rule": FileTypeMatch("price_rule", "Price Rule", "badge-rule", [".xml"], ["PricingRule", "priceActions", "conditions"]),
    "product_rule": FileTypeMatch("product_rule", "Product Rule", "badge-rule", [".xml"], ["ProductRule", "productRuleType", "errorConditionMet"]),
    "lookup_table": FileTypeMatch("lookup_table", "Lookup Table", "badge-xml", [".xml"], ["LookupTable", "SBQQ__LookupTable"]),
    "summary_variable": FileTypeMatch("summary_variable", "Summary Var", "badge-xml", [".xml"], ["SummaryVariable", "SBQQ__SummaryVariable"]),
    "object_metadata": FileTypeMatch("object_metadata", "Object Meta", "badge-meta", [".object-meta.xml"], ["CustomObject", "<fields>"]),
    "xml_generic": FileTypeMatch("xml_generic", "XML Metadata", "badge-xml", [".xml", ".resource"], []),
    "unknown": FileTypeMatch("unknown", "Unknown", "badge-unknown", [], []),
    "bundle": FileTypeMatch("bundle", "Bundle", "badge-rule", [".xml"], ["ProductOption", "ProductFeature"]),
    "constraint": FileTypeMatch("constraint", "Option Constraint", "badge-rule", [".xml"], ["Constraint", "OptionConstraint"]),
    "discount_schedule": FileTypeMatch("discount_schedule", "Discount Schedule", "badge-rule", [".xml"], ["DiscountSchedule", "DiscountTier"]),
    "approval_rule": FileTypeMatch("approval_rule", "Approval Rule", "badge-rule", [".xml"], ["ApprovalCondition", "ApprovalRule"]),
    "quote_template": FileTypeMatch("quote_template", "Quote Template", "badge-meta", [".xml"], ["QuoteTemplate"]),
}

QCP_HOOKS: list[str] = [
    "onInit",
    "onBeforeCalculate",
    "onCalculate",
    "onAfterCalculate",
    "onBeforePriceRules",
    "onAfterPriceRules",
    "onAfterFinalCalc",
]

SBQQ_TO_RCA_OBJECT_MAP: dict[str, str] = {
    "SBQQ__Quote__c": "SalesTransaction",
    "SBQQ__QuoteLine__c": "SalesTransactionItem",
    "SBQQ__Subscription__c": "Asset",
    "SBQQ__ProductOption__c": "ProductComponent",
    "SBQQ__PriceRule__c": "Pricing Procedure Step",
}
