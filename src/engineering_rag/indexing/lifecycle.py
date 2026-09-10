'''Document update, delete, rollback, and recovery helpers.'''


def recover_active_snapshot() -> str | None:
    '''Recover the last valid active snapshot after a restart.'''
    raise NotImplementedError('Snapshot recovery is planned for M5.')

