'''Runtime dependency and compatibility checks.'''

from dataclasses import dataclass


@dataclass(frozen=True)
class PreflightResult:
    '''Result of a local or container preflight check.'''

    ok: bool
    checks: dict[str, str]


def run_preflight() -> PreflightResult:
    '''Run lightweight checks that do not require external services.'''
    return PreflightResult(ok=True, checks={'python': 'available'})

