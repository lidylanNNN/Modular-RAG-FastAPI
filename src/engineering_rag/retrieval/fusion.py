'''Candidate fusion helpers.'''

from engineering_rag.contracts.retrieval import Candidate


def reciprocal_rank_fusion(candidates: list[Candidate], k: int = 60) -> list[Candidate]:
    '''Fuse BM25 and dense candidates using reciprocal rank fusion.'''
    raise NotImplementedError('RRF fusion is planned for M6.')

