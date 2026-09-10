'''Reranker skeleton.'''

from engineering_rag.contracts.retrieval import Candidate, FinalCandidate, SearchQuery


def rerank(query: SearchQuery, candidates: list[Candidate]) -> list[FinalCandidate]:
    '''Rerank fused candidates into the final top-k evidence list.'''
    raise NotImplementedError('Reranking is planned for M7.')

