'''目录迁移的回归检查：从仓库外调用，以及构建后保持数据身份。'''

import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.evaluation import build_expansion

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
EVALUATION_ROOT = REPOSITORY_ROOT / 'evaluation'


def dataset_hashes(base: Path) -> dict[str, str]:
    '''汇总原件、清单和机器标注字节哈希，忽略展示文档。'''
    return {
        path.relative_to(base).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (base / 'datasets').rglob('*')
        if path.is_file() and path.suffix in {'.docx', '.xlsx', '.json', '.jsonl'}
    }


class RepositoryLayoutTests(unittest.TestCase):
    def test_cli_outside_repository(self) -> None:
        '''脚本默认数据路径不受调用方当前工作目录影响。'''
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, '-X', 'utf8', str(REPOSITORY_ROOT / 'scripts/evaluation/validate_suite.py')],
                cwd=directory, capture_output=True, text=True, encoding='utf-8', timeout=30, check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"split_identity_checks": "passed"', result.stdout)

    def test_rebuild_keeps_dataset_identity(self) -> None:
        '''在临时副本重建机器草案后，原件与标注必须保持逐字节一致。'''
        expected = dataset_hashes(EVALUATION_ROOT)
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / 'evaluation'
            shutil.copytree(EVALUATION_ROOT, base)
            with patch.object(build_expansion, 'ROOT', base), patch.object(build_expansion, 'OLD', base / 'datasets/archive/synthetic-v1'):
                build_expansion.build('dev')
                build_expansion.build('validation')
            self.assertEqual(expected, dataset_hashes(base))


if __name__ == '__main__':
    unittest.main()
