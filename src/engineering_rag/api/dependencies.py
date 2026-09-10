'''FastAPI dependency providers.'''


def get_application_context() -> object:
    '''Return the shared application context for HTTP handlers.'''
    raise NotImplementedError('API dependencies are planned for M10.')

