'''Base chunker contract.'''

from typing import Protocol

from engineering_rag.contracts.chunk import Chunk


class Chunker(Protocol):
    '''Protocol implemented by each source-unit chunking strategy.'''

    def chunk(self, source_units: list[dict]) -> list[Chunk]:
        '''Convert canonical source units into unified chunks.'''
        ...

