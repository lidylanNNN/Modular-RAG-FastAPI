'''校验当前开发/验证套件的数量、原文件证据和文档族隔离，不计算模型效果。'''

import json
import sys
import unicodedata
from pathlib import Path

if __package__:
    from .validate_dataset import load_lines, require, validate
else:
    from validate_dataset import load_lines, require, validate

VALIDATION_BUILD_ROOT = Path(__file__).resolve().parents[2] / 'validation_build'


def validate_suite(base: Path) -> dict:
    '''按协议检查所有活动数据集；跨 split 的身份或问题重复会导致失败。'''
    protocol = json.loads((base / 'protocols/development.json').read_text(encoding='utf-8'))
    seen = {name: {} for name in ('leakage_group', 'document_id', 'content_hash', 'normalized_question')}
    reports = []
    for entry in protocol['datasets']:
        folder = (base / entry['path']).resolve()
        require(folder.is_relative_to(base.resolve()), 'dataset path escapes validation_build')
        report = validate(folder)
        require(report['split'] == entry['split'], 'split mismatch')
        for key, expected_key in [('cases', 'expected_cases'), ('answerable', 'expected_answerable'),
                                  ('source_files', 'expected_sources'), ('source_units', 'expected_units')]:
            require(report[key] == entry[expected_key], f'{entry["path"]}: unexpected {key}')
        manifest = json.loads((folder / 'corpus_manifest.json').read_text(encoding='utf-8'))
        notes, cases = load_lines(folder / 'annotations.jsonl'), load_lines(folder / 'cases.jsonl')
        values = {
            'leakage_group': {note['leakage_group'] for note in notes},
            'document_id': {source['document_id'] for source in manifest['sources']},
            'content_hash': {source['content_hash'] for source in manifest['sources']},
            'normalized_question': {''.join(unicodedata.normalize('NFKC', case['question']).casefold().split()) for case in cases},
        }
        for category, items in values.items():
            for item in items:
                prior = seen[category].get(item)
                require(prior is None or prior == entry['split'], f'cross-split leakage: {category}')
                seen[category][item] = entry['split']
        reports.append({'dataset': entry['path'], **report})
    return {'datasets': reports, 'split_identity_checks': 'passed', 'near_duplicate_human_review': 'pending',
            'model_evaluation': 'not_run', 'release_ready': False}


if __name__ == '__main__':
    try:
        print(json.dumps(validate_suite(VALIDATION_BUILD_ROOT), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError) as error:
        print(f'INVALID SUITE: {error}', file=sys.stderr)
        sys.exit(1)
