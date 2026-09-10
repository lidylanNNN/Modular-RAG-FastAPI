'''Health check route skeleton.'''


def health() -> dict[str, str]:
    '''Return service health status.'''
    return {'status': 'ok'}

