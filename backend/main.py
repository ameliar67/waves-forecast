import asyncio
import datetime
import logging
import signal

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
    logging.getLogger("aiohttp.client").setLevel(logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.DEBUG)

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

    try:
        wait_task = asyncio.Future()
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, wait_task.cancel)
        loop.add_signal_handler(signal.SIGTERM, wait_task.cancel)

        await wait_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
