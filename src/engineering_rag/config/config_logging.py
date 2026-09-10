'''Logging configuration helpers.'''

import logging


def configure_logging(level: int = logging.INFO) -> None:
    '''Configure a minimal structured logging baseline for local development.'''
    logging.basicConfig(level=level, format='%(asctime)s %(levelname)s %(name)s %(message)s')

