'''校验器回归测试使用临时副本，避免修改评测原件。'''

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_dataset import validate


class DatasetValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        '''复制旧开发夹具，用于独立构造有效及无效标注。'''
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'dataset'
        shutil.copytree(Path(__file__).parent / 'dev/synthetic-v1', self.root)
        self.cases = self.read_lines('cases.jsonl')
        self.notes = self.read_lines('annotations.jsonl')

    def read_lines(self, name: str) -> list[dict]:
        '''读取临时夹具中的逐行 JSON 对象。'''
        return [json.loads(line) for line in (self.root / name).read_text(encoding='utf-8').splitlines()]

    def save(self) -> None:
        '''保存当前测试所需的题目和复核记录。'''
        for name, rows in [('cases.jsonl', self.cases), ('annotations.jsonl', self.notes)]:
            (self.root / name).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows), encoding='utf-8')

    def test_accepts_variable_case_count(self) -> None:
        '''有效数据集不依赖旧夹具的二十题或题型配额。'''
        self.cases, self.notes = self.cases[:1], self.notes[:1]
        self.save()
        self.assertEqual(validate(self.root)['cases'], 1)

    def test_rejects_evidence_outside_file_filter(self) -> None:
        '''仅允许 XLSX 时不得用 DOCX 原文作为答案证据。'''
        self.cases[0]['filters'] = {'file_types': ['xlsx']}
        self.save()
        with self.assertRaisesRegex(ValueError, 'filter'):
            validate(self.root)

    def test_rejects_review_without_reviewer(self) -> None:
        '''禁止只改状态就把未经登记的标注当作人工复核完成。'''
        self.notes[0]['human_review_status'] = 'reviewed'
        self.save()
        with self.assertRaisesRegex(ValueError, 'review'):
            validate(self.root)

    def test_reports_actual_review_status(self) -> None:
        '''复核汇总来自实际记录，不硬编码为 pending。'''
        self.cases, self.notes = self.cases[:1], self.notes[:1]
        self.notes[0].update(human_review_status='reviewed', reviewer='unit-test-only',
                             reviewed_at='2026-09-08T00:00:00+00:00', review_notes='仅用于测试状态汇总')
        self.save()
        self.assertEqual(validate(self.root)['human_review'], 'reviewed')

    def test_rejects_out_of_bounds_span(self) -> None:
        '''证据区间超出真实原文长度时必须失败。'''
        self.cases[0]['evidence_groups'][0]['alternatives'][0]['source_spans'][0]['char_end'] = 99999
        self.save()
        with self.assertRaisesRegex(ValueError, 'span'):
            validate(self.root)

    def test_rejects_duplicate_case(self) -> None:
        '''重复题号不能掩盖缺失题目。'''
        self.cases[1]['case_id'] = self.cases[0]['case_id']
        self.save()
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate(self.root)

    def test_rejects_unknown_filter(self) -> None:
        '''未知过滤字段不能被静默忽略。'''
        self.cases[0]['filters'] = {'arbitrary_es_query': '*'}
        self.save()
        with self.assertRaisesRegex(ValueError, 'filter'):
            validate(self.root)

    def test_rejects_mismatched_sheet(self) -> None:
        '''实际属于失效案例表的证据不能通过另一张表的过滤。'''
        self.cases[8]['filters'] = {'sheet': '不存在的工作表'}
        self.save()
        with self.assertRaisesRegex(ValueError, 'sheet filter'):
            validate(self.root)

    def test_rejects_missing_conflict_evidence(self) -> None:
        '''冲突拒答必须附至少两条可核对的矛盾原文锚点。'''
        self.cases[-1]['expected_refusal_reason'] = 'version_conflict'
        self.save()
        with self.assertRaisesRegex(ValueError, 'conflict anchors'):
            validate(self.root)

    def test_rejects_original_file_changes(self) -> None:
        '''原件字节变化必须使旧清单失效。'''
        source = next((self.root / 'corpus').glob('*.docx'))
        source.write_bytes(source.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, '哈希'):
            validate(self.root)


if __name__ == '__main__':
    unittest.main()
