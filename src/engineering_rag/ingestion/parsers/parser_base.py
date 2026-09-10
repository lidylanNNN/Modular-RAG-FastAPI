'''Base parser contract.'''

from pathlib import Path
from typing import Protocol


class Parser(Protocol):
    '''Protocol implemented by each file format parser.'''

    def parse(self, path: Path) -> list[dict]:
        '''Parse a source document into canonical source units.'''
        ...

