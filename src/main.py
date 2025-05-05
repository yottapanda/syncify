import time
from multiprocessing import Process
import signal
import sys

from src import alembic
from src.common import conf
from src.webapp.app import app
import uvicorn
from src.worker import worker


def start_webapp():
    uvicorn.run(app, host=conf.host, port=conf.port, workers=1)


def start_worker():
    print("Starting worker...")
    while True:
        time.sleep(1)
        try:
            worker.run()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping worker...")
            break
        except Exception as e:
            print(f"Exception: {e}")
            continue


def signal_handler(sig, frame):
    print("\nShutting down all processes...")
    sys.exit(0)


if __name__ == "__main__":
    alembic.check()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Create processes
    webapp_process = Process(target=start_webapp)
    worker_process = Process(target=start_worker)

    # Start both processes
    print("Starting webapp and worker...")
    webapp_process.start()
    worker_process.start()

    # Wait for processes to complete (they will run until interrupted)
    webapp_process.join()
    worker_process.join()
