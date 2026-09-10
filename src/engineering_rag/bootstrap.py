'''Application bootstrap and dependency assembly.'''

from dataclasses import dataclass

from engineering_rag.config.settings import Settings, load_settings


@dataclass(frozen=True)
class ApplicationContext:
    '''Container for shared application dependencies.'''

    settings: Settings


def build_application_context() -> ApplicationContext:
    '''Build the dependency context used by CLI, API, tests, and tools.'''
    return ApplicationContext(settings=load_settings())

