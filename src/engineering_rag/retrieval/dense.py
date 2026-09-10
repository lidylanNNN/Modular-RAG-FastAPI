'''Dense vector retrieval skeleton.'''

from engineering_rag.contracts.retrieval import Candidate, SearchQuery


def retrieve_dense(query: SearchQuery) -> list[Candidate]:
    '''Retrieve candidate chunks with dense vector search from the active snapshot.'''
    raise NotImplementedError('Dense retrieval is planned for M5.')

