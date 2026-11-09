"""Read-only lexical provenance checkpoint for Spek.

Spek composes *realized, paired* SemantiK results. A diK/WordBench lexical
candidate can never be used as a Spek realization or publication approval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .core import ValidationError


ALLOWED = {'dik.semantik-knowledge-handoff/1.0-candidate',
           'gf-wordbench.dik-semantik-lexicon/1.0-candidate'}


def inspect_lexical_dependency(bundle: Path) -> dict[str, Any]:
    bundle = Path(bundle)
    if bundle.is_symlink() or not bundle.is_dir():
        raise ValidationError('Répertoire lexical candidat absent ou lien symbolique')
    path = bundle/'manifest.json'
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 100000:
        raise ValidationError('Manifeste lexical candidat absent ou trop volumineux')
    report = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(report, dict) or report.get('schema_id') not in ALLOWED or report.get('released') is not False:
        raise ValidationError('Spek refuse un artefact lexical inconnu ou présenté comme publié')
    is_dik = report['schema_id'].startswith('dik.')
    name = 'semantik.knowledge.json' if is_dik else 'lexicon.candidate.json'
    artifact = bundle/name
    if artifact.is_symlink() or not artifact.is_file() or artifact.stat().st_size > 100*1024*1024:
        raise ValidationError('Artefact lexical absent ou non sûr')
    sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if sha != report.get('lexicon_sha256'):
        raise ValidationError('Empreinte lexicale incompatible')
    if (is_dik and report.get('gf_bindings',0) != 0) or (not is_dik and report.get('gf_verified') is not False):
        raise ValidationError('Qualification lexicale candidate incohérente')
    return {'schema_id':'spek.lexical-dependency-inspection/1.0',
            'status':'LEXICAL_DEPENDENCY_CANDIDATE_ONLY', 'source_schema_id':report['schema_id'],
            'lexicon_sha256':sha, 'language':report['locale'],
            'knowledge_entries':report['entries'] if is_dik else report['knowledge_entries'],
            'candidate_bindings':0 if is_dik else report['human_reviewed_binding_candidates'],
            'realizations_imported':0, 'publication_eligible':False,
            'notice':'Only actual request/result pairs from SemantiK Architect may be imported as realizations.'}
