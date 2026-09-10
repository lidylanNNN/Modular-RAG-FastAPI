'''BM25 retrieval skeleton.'''

from engineering_rag.contracts.retrieval import Candidate, SearchQuery


def retrieve_bm25(query: SearchQuery) -> list[Candidate]:
    '''Retrieve candidate chunks with BM25 from the active snapshot.'''
    raise NotImplementedError('BM25 retrieval is planned for M4.')

