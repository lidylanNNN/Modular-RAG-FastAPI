'''Request-local source binding.'''

from engineering_rag.contracts.retrieval import FinalCandidate


def bind_sources(candidates: list[FinalCandidate]) -> dict[str, FinalCandidate]:
    '''Assign request-local source IDs to final candidates.'''
    raise NotImplementedError('Source binding is planned for M8.')

