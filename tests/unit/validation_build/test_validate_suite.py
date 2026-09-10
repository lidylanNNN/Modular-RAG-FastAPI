'''检查整套数据集的正向验收和跨集合泄漏拦截。'''

import json
import shutil
from pathlib import Path

import pytest

from scripts.validation_build.validate_suite import VALIDATION_BUILD_ROOT, validate_suite


def test_active_suite() -> None:
    '''实际两套资料应通过结构、原文和身份隔离检查。'''
    result = validate_suite(VALIDATION_BUILD_ROOT)
    assert [item['cases'] for item in result['datasets']] == [40, 12]
    assert result['release_ready'] is False


def test_cross_split_family_is_rejected(tmp_path: Path) -> None:
    '''人为把验证题放进开发文档族时必须识别泄漏。'''
    base = VALIDATION_BUILD_ROOT
    root = tmp_path
    (root / 'protocols').mkdir()
    shutil.copyfile(base / 'protocols/development.json', root / 'protocols/development.json')
    for relative in ('datasets/dev/synthetic-v2', 'datasets/validation/synthetic-cooling-v1'):
        shutil.copytree(base / relative, root / relative)
    path = root / 'datasets/validation/synthetic-cooling-v1/annotations.jsonl'
    notes = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    notes[0]['leakage_group'] = 'synthetic-control-family'
    path.write_text(''.join(json.dumps(note, ensure_ascii=False) + '\n' for note in notes), encoding='utf-8')
    with pytest.raises(ValueError, match='cross-split leakage'):
        validate_suite(root)
