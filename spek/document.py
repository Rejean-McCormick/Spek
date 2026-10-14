"""Immutable, language-specific presentation projection.

This is a derived document model, NOT a Kristal canonical state. Renderers
consume the same projection and may not silently omit semantic identities.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
from .core import Compiled


@dataclass(frozen=True)
class DocumentItem:
    id: str
    kind: str
    text: str
    status: str
    evidence_refs: tuple[str, ...]
    locator: str

    def trace(self) -> str:
        parts = [self.id, self.kind, self.status]
        if self.evidence_refs:
            parts.append('refs: ' + ', '.join(self.evidence_refs))
        if self.locator:
            parts.append('locator: ' + self.locator)
        return ' · '.join(parts)

    def to_dict(self) -> dict:
        return dict(id=self.id, kind=self.kind, text=self.text, status=self.status,
                    evidence_refs=list(self.evidence_refs), locator=self.locator)


@dataclass(frozen=True)
class DocumentSection:
    id: str
    layout: str
    layout_version: str
    heading: str
    slots: Mapping[str, tuple[DocumentItem, ...]]

    def items(self, slot: str) -> tuple[DocumentItem, ...]:
        return self.slots.get(slot, ())

    def to_dict(self) -> dict:
        return dict(id=self.id, layout=self.layout, layout_version=self.layout_version,
                    heading=self.heading,
                    slots={slot: [item.to_dict() for item in entries]
                           for slot, entries in self.slots.items()})


@dataclass(frozen=True)
class SpekDocument:
    language: str
    article_id: str
    title: str
    subtitle: str
    abstract: str
    demonstration: bool
    source_verified: bool
    source_sha256: str
    realizations_sha256: str
    layouts_sha256: str
    sections: tuple[DocumentSection, ...]

    def to_dict(self) -> dict:
        return dict(format='spek.document/0.2', language=self.language, article_id=self.article_id,
                    title=self.title, subtitle=self.subtitle, abstract=self.abstract,
                    demonstration=self.demonstration, source_verified=self.source_verified,
                    source_sha256=self.source_sha256, realizations_sha256=self.realizations_sha256,
                    layouts_sha256=self.layouts_sha256,
                    sections=[section.to_dict() for section in self.sections])


def project_document(model: Compiled, language: str) -> SpekDocument:
    if language not in model.languages:
        raise ValueError('Language not validated in model: ' + language)
    sections = []
    for section in model.sections:
        slots = {}
        for slot in model.layouts[section['layout']]['slots']:
            entries = []
            for source in model.slot_items(section, slot, language):
                entries.append(DocumentItem(
                    id=source['id'], kind=source['kind'], text=source['text'],
                    status=source.get('epistemic_status') or 'unspecified',
                    evidence_refs=tuple(source.get('evidence_refs') or ()),
                    locator=source.get('locator') or ''))
            slots[slot] = tuple(entries)
        sections.append(DocumentSection(id=section['id'],layout=section['layout'],
                         layout_version=model.layouts[section['layout']]['version'],
                         heading=model.text(section['heading_key'], language),slots=slots))
    article=model.source['article']
    return SpekDocument(language=language, article_id=article['id'],
       title=model.text(article['title_key'],language),
       subtitle=model.text(article['subtitle_key'],language),
       abstract=model.text(article['abstract_key'],language),
       demonstration=model.demo, source_verified=model.source_verified,
       source_sha256=model.source_hash, realizations_sha256=model.realization_hash,
       layouts_sha256=model.layout_hash, sections=tuple(sections))
