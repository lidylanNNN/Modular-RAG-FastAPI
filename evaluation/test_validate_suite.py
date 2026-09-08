'''检查整套数据集的正向验收和跨集合泄漏拦截。'''

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_suite import validate_suite


class SuiteValidationTests(unittest.TestCase):
    def test_active_suite(self) -> None:
        '''实际两套资料应通过结构、原文和身份隔离检查。'''
        result = validate_suite(Path(__file__).parent)
        self.assertEqual([item['cases'] for item in result['datasets']], [40, 12])
        self.assertFalse(result['release_ready'])

    def test_cross_split_family_is_rejected(self) -> None:
        '''人为把验证题放进开发文档族时必须识别泄漏。'''
        base = Path(__file__).parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copyfile(base / 'eval_protocol.json', root / 'eval_protocol.json')
            for relative in ('dev/synthetic-v2', 'validation/synthetic-cooling-v1'):
                shutil.copytree(base / relative, root / relative)
            path = root / 'validation/synthetic-cooling-v1/annotations.jsonl'
            notes = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
            notes[0]['leakage_group'] = 'synthetic-control-family'
            path.write_text(''.join(json.dumps(note, ensure_ascii=False) + '\n' for note in notes), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'cross-split leakage'):
                validate_suite(root)


if __name__ == '__main__':
    unittest.main()
