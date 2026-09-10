'''目录迁移的回归检查：从仓库外调用，以及构建后保持数据身份。'''

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.validation_build import build_expansion

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
VALIDATION_BUILD_ROOT = REPOSITORY_ROOT / 'validation_build'


def dataset_hashes(base: Path) -> dict[str, str]:
    '''汇总原件、清单和机器标注字节哈希，忽略展示文档。'''
    return {
        path.relative_to(base).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (base / 'datasets').rglob('*')
        if path.is_file() and path.suffix in {'.docx', '.xlsx', '.json', '.jsonl'}
    }


def test_cli_outside_repository(tmp_path: Path) -> None:
    '''脚本默认数据路径不受调用方当前工作目录影响。'''
    result = subprocess.run(
        [sys.executable, '-X', 'utf8', str(REPOSITORY_ROOT / 'scripts/validation_build/validate_suite.py')],
        cwd=tmp_path, capture_output=True, text=True, encoding='utf-8', timeout=30, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert '"split_identity_checks": "passed"' in result.stdout


def test_rebuild_keeps_dataset_identity(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    '''在临时副本重建机器草案后，原件与标注必须保持逐字节一致。'''
    expected = dataset_hashes(VALIDATION_BUILD_ROOT)
    base = tmp_path / 'validation_build'
    shutil.copytree(VALIDATION_BUILD_ROOT, base)
    monkeypatch.setattr(build_expansion, 'ROOT', base)
    monkeypatch.setattr(build_expansion, 'OLD', base / 'datasets/archive/synthetic-v1')
    build_expansion.build('dev')
    build_expansion.build('validation')
    assert expected == dataset_hashes(base)
