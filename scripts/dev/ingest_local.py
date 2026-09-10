'''Local document ingestion command.'''

from pathlib import Path
import sys

from engineering_rag.services.document_service import ingest


def main(argv: list[str] | None = None) -> None:
    '''Ingest one local document path for development testing.'''
    args = sys.argv[1:] if argv is None else argv
    if not args:
        raise SystemExit('usage: python -m scripts.dev.ingest_local <document-path>')
    print(ingest(Path(args[0])))


if __name__ == '__main__':
    main()

