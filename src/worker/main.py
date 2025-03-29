import signal

from src import alembic

if __name__ == "__main__":
    alembic.check()

    from src.worker.worker import WorkerThread

    worker = WorkerThread()
    worker.start()

    original_int_handler = signal.getsignal(signal.SIGINT)


    def sigint_handler(signum, frame):
        worker.stop()
        if worker.is_alive():
            worker.join()
        original_int_handler(signum, frame)


    try:
        signal.signal(signal.SIGINT, sigint_handler)
    except ValueError as e:
        print(f'{e}. Continuing execution...')
