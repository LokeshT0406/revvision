from __future__ import annotations

from revvision.constants import FILE_TYPE_RULES
from revvision.types import FileTypeMatch


def detect_file_type(filename: str, content: str) -> FileTypeMatch:
    name = filename.lower()
    for key, rule in FILE_TYPE_RULES.items():
        if key in {"xml_generic", "unknown"}:
            continue
        if any(name.endswith(ext) for ext in rule.extensions):
            if not rule.keywords or any(k.lower() in content.lower() for k in rule.keywords):
                return rule

    if name.endswith((".cls", ".apex")):
        return FILE_TYPE_RULES["apex_class"]
    if name.endswith(".trigger"):
        return FILE_TYPE_RULES["apex_trigger"]
    if name.endswith((".flow", ".flow-meta.xml")):
        return FILE_TYPE_RULES["flow"]
    if name.endswith(".js"):
        return FILE_TYPE_RULES["qcp"]
    if name.endswith((".xml", ".resource")):
        return FILE_TYPE_RULES["xml_generic"]
    return FILE_TYPE_RULES["unknown"]
