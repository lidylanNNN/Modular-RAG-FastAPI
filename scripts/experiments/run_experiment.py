'''Evaluation experiment command.'''

from pathlib import Path
import sys

from engineering_rag.services.evaluation_service import run_evaluation


def main(argv: list[str] | None = None) -> None:
    '''Run an evaluation protocol through the application service layer.'''
    args = sys.argv[1:] if argv is None else argv
    protocol = Path(args[0]) if args else Path('validation_build/protocols/development.json')
    print(run_evaluation(str(protocol)))


if __name__ == '__main__':
    main()

