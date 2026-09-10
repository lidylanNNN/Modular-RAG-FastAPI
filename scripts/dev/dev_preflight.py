'''Development preflight command.'''

from engineering_rag.config.preflight import run_preflight


def main() -> None:
    '''Run local development preflight checks and print the result.'''
    result = run_preflight()
    print(result)


if __name__ == '__main__':
    main()

