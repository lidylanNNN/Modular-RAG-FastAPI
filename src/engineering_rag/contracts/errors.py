'''Shared application error types.'''


class EngineeringRagError(Exception):
    '''Base class for expected application errors.'''


class ConfigurationError(EngineeringRagError):
    '''Raised when runtime configuration is incomplete or invalid.'''


class RetrievalFailure(EngineeringRagError):
    '''Raised when retrieval cannot complete according to the active profile.'''


class ContextBudgetExceeded(EngineeringRagError):
    '''Raised when no candidate can fit into the generation context budget.'''

