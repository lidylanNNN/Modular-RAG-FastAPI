'''校验器回归测试使用临时副本，避免修改评测原件。'''

import json
import shutil
from pathlib import Path

import pytest

from scripts.validation_build.validate_dataset import validate

VALIDATION_BUILD_ROOT = Path(__file__).resolve().parents[3] / 'validation_build'


class DatasetCopy:
    def __init__(self, root: Path) -> None:
        '''Load a writable dataset copy for one pytest case.'''
        self.root = root
        self.cases = self.read_lines('cases.jsonl')
        self.notes = self.read_lines('annotations.jsonl')

    def read_lines(self, name: str) -> list[dict]:
        '''读取临时夹具中的逐行 JSON 对象。'''
        return [json.loads(line) for line in (self.root / name).read_text(encoding='utf-8').splitlines()]

    def save(self) -> None:
        '''保存当前测试所需的题目和复核记录。'''
        for name, rows in [('cases.jsonl', self.cases), ('annotations.jsonl', self.notes)]:
            (self.root / name).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows), encoding='utf-8')


@pytest.fixture
def dataset(tmp_path: Path) -> DatasetCopy:
    '''复制旧开发夹具，用于独立构造有效及无效标注。'''
    root = tmp_path / 'dataset'
    shutil.copytree(VALIDATION_BUILD_ROOT / 'datasets/archive/synthetic-v1', root)
    return DatasetCopy(root)


def test_accepts_variable_case_count(dataset: DatasetCopy) -> None:
    '''有效数据集不依赖旧夹具的二十题或题型配额。'''
    dataset.cases, dataset.notes = dataset.cases[:1], dataset.notes[:1]
    dataset.save()
    assert validate(dataset.root)['cases'] == 1


def test_rejects_evidence_outside_file_filter(dataset: DatasetCopy) -> None:
    '''仅允许 XLSX 时不得用 DOCX 原文作为答案证据。'''
    dataset.cases[0]['filters'] = {'file_types': ['xlsx']}
    dataset.save()
    with pytest.raises(ValueError, match='filter'):
        validate(dataset.root)


def test_rejects_review_without_reviewer(dataset: DatasetCopy) -> None:
    '''禁止只改状态就把未经登记的标注当作人工复核完成。'''
    dataset.notes[0]['human_review_status'] = 'reviewed'
    dataset.save()
    with pytest.raises(ValueError, match='review'):
        validate(dataset.root)


def test_reports_actual_review_status(dataset: DatasetCopy) -> None:
    '''复核汇总来自实际记录，不硬编码为 pending。'''
    dataset.cases, dataset.notes = dataset.cases[:1], dataset.notes[:1]
    dataset.notes[0].update(human_review_status='reviewed', reviewer='unit-test-only',
                            reviewed_at='2026-09-08T00:00:00+00:00', review_notes='仅用于测试状态汇总')
    dataset.save()
    assert validate(dataset.root)['human_review'] == 'reviewed'


def test_rejects_out_of_bounds_span(dataset: DatasetCopy) -> None:
    '''证据区间超出真实原文长度时必须失败。'''
    dataset.cases[0]['evidence_groups'][0]['alternatives'][0]['source_spans'][0]['char_end'] = 99999
    dataset.save()
    with pytest.raises(ValueError, match='span'):
        validate(dataset.root)


def test_rejects_duplicate_case(dataset: DatasetCopy) -> None:
    '''重复题号不能掩盖缺失题目。'''
    dataset.cases[1]['case_id'] = dataset.cases[0]['case_id']
    dataset.save()
    with pytest.raises(ValueError, match='duplicate'):
        validate(dataset.root)


def test_rejects_unknown_filter(dataset: DatasetCopy) -> None:
    '''未知过滤字段不能被静默忽略。'''
    dataset.cases[0]['filters'] = {'arbitrary_es_query': '*'}
    dataset.save()
    with pytest.raises(ValueError, match='filter'):
        validate(dataset.root)


def test_rejects_mismatched_sheet(dataset: DatasetCopy) -> None:
    '''实际属于失效案例表的证据不能通过另一张表的过滤。'''
    dataset.cases[8]['filters'] = {'sheet': '不存在的工作表'}
    dataset.save()
    with pytest.raises(ValueError, match='sheet filter'):
        validate(dataset.root)


def test_rejects_missing_conflict_evidence(dataset: DatasetCopy) -> None:
    '''冲突拒答必须附至少两条可核对的矛盾原文锚点。'''
    dataset.cases[-1]['expected_refusal_reason'] = 'version_conflict'
    dataset.save()
    with pytest.raises(ValueError, match='conflict anchors'):
        validate(dataset.root)


def test_rejects_original_file_changes(dataset: DatasetCopy) -> None:
    '''原件字节变化必须使旧清单失效。'''
    source = next((dataset.root / 'corpus').glob('*.docx'))
    source.write_bytes(source.read_bytes() + b'changed')
    with pytest.raises(ValueError, match='哈希'):
        validate(dataset.root)
