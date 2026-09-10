'''Metric recording helpers.'''


def record_latency(metric_name: str, milliseconds: float) -> dict:
    '''Create a latency metric payload for later reporting.'''
    return {'metric': metric_name, 'milliseconds': milliseconds}

