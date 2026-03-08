from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FileTypeMatch:
    type_key: str
    label: str
    badge: str
    extensions: list[str]
    keywords: list[str]


@dataclass
class ParseResult:
    conditions: int = 0
    actions: int = 0
    lookups: int = 0
    summary_vars: int = 0
    hardcoded_ids: int = 0
    soql_hits: int = 0
    qcp: bool = False
    score: int = 0
    insights: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssessedArtifact:
    file_name: str
    type_label: str
    type_key: str
    badge: str
    score: int
    risk: str
    est_weeks: float
    qcp: bool
    conditions: int
    actions: int
    lookups: int
    summary_vars: int
    hardcoded_ids: int
    soql_hits: int
    insights: list[str]
    raw: str
    extra: dict[str, Any]
