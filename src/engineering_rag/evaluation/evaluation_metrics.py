'''Evaluation metric calculations.'''


def recall_at_k(matches: list[bool], k: int) -> float:
    '''Calculate recall at a fixed candidate cutoff.'''
    if k <= 0:
        return 0.0
    return 1.0 if any(matches[:k]) else 0.0

