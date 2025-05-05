import time

from src import alembic
from src.worker import worker

if __name__ == "__main__":
    alembic.check()

    print("Starting worker...")
    while True:
        time.sleep(1)
        # noinspection PyBroadException
        try:
            worker.run()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping worker...")
            break
        except Exception as e:
            print(f"Exception: {e}")
            continue
