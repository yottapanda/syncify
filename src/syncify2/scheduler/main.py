import time
from datetime import datetime

from syncify2.common import alembic
from syncify2.common import conf
from syncify2.scheduler import scheduler

if __name__ == "__main__":
    alembic.check()

    print("Starting scheduler...")

    last_run = datetime.min
    while True:
        try:
            if datetime.now() > last_run + conf.scheduler_interval:
                last_run = datetime.now()
                scheduler.run()
            time.sleep(5)
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping scheduler...")
            break
        except Exception as e:
            print(f"Exception: {e}")
            continue
