# -*- coding: utf-8 -*-
"""Verification locale non destructive des fichiers necessaires au demarrage.

Usage : py -3 VERIFIER_INSTALLATION_SPEK.py
"""
from __future__ import annotations
from pathlib import Path
import sys

REQUIRED = (
    'core', 'kristal_identity', 'local_kristals',
    'studio_gui', 'studio_view_model', 'studio_workflow',
    'ai_proposals', 'composition_registry', 'source_reviews',
    'structural_preview', 'semantik_execution', 'semantik_transfer',
    'template_manager', 'template_library', 'branding',
)


def check(root: Path) -> list[str]:
    root = Path(root)
    missing = [f'spek/{name}.py' for name in REQUIRED
               if not (root/'spek'/f'{name}.py').is_file()]
    for extra in ('Spek_Template_Manager.pyw','layouts','template_library'):
        if not (root/extra).exists():
            missing.append(extra)
    return missing


def main() -> int:
    root = Path(__file__).resolve().parent
    missing = check(root)
    print('Depot Spek :', root)
    if missing:
        print('INSTALLATION INCOMPLETE :')
        for name in missing:
            print(' -', name)
        print('Applique le correctif de reparation dans le dossier parent de Spek.')
        return 1
    print('OK - tous les fichiers de demarrage sont presents.')
    print('Ce controle ne certifie pas les RuntimeSets SemantiK ni la publication Wiki.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
