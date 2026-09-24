"""Upgrade legacy source classification without retaining redundant fields."""
from src.models.domain import SourceType


def migrated_type(source_type, evidence_label):
    kind = SourceType(source_type)
    label = (evidence_label or '').lower()
    if kind == SourceType.ARTICLE:
        if 'research' in label or 'report' in label:
            return SourceType.RESEARCH
        if 'standard' in label or 'guidance' in label or 'framework' in label:
            return SourceType.FRAMEWORK
        if 'catalogue' in label or 'training' in label:
            return SourceType.CATALOGUE
    return kind
