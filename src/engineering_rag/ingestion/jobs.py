'''Persistent ingestion job state machine.'''


def enqueue_ingestion_job(document_path: str) -> str:
    '''Create an ingestion job for asynchronous API processing.'''
    raise NotImplementedError('Persistent ingestion jobs are planned for M10.')

