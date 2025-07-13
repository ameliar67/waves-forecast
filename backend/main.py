import asyncio
import datetime
import logging

from apscheduler.events import JobExecutionEvent, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

from config import Config


def on_scheduler_executed(event: JobExecutionEvent):
    if event.exception:
        logging.exception("Job execution failed", exc_info=event.exception)
    else:
        logging.info("Job executed successfully")


async def main():
    from function_app import refresh_api_data

    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    app_config = Config.from_environment()

    scheduler = AsyncIOScheduler()
    scheduler.add_listener(on_scheduler_executed, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.add_job(
        refresh_api_data,
        args=[app_config],
        trigger=CronTrigger(
            hour=4,
            minute=15,
            timezone=datetime.timezone.utc,
        ),
    )

    scheduler.start()


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        logging.info("Exiting")
