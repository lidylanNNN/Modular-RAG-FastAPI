'''Logging field helpers.'''


def bind_trace_fields(trace_id: str) -> dict[str, str]:
    '''Return logging fields shared by trace-aware log records.'''
    return {'trace_id': trace_id}

