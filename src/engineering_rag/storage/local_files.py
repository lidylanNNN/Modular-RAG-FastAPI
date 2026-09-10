'''Local runtime file storage helpers.'''

from pathlib import Path


def document_store(data_dir: Path) -> Path:
    '''Return the local document storage directory.'''
    return data_dir / 'documents'


def parsed_store(data_dir: Path) -> Path:
    '''Return the local parsed-artifact storage directory.'''
    return data_dir / 'parsed'

