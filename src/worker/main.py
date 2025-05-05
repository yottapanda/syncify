import time

from src import alembic
from src.worker import worker

if __name__ == "__main__":
    alembic.check()

    print("Starting worker...")
    while True:
        try:
            worker.run()
            time.sleep(1)
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping worker...")
            break
        except Exception as e:
            print(f"Exception: {e}")
            continue
