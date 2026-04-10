# main.py

# APScheduler: runs our agent automatically every X minutes
from apscheduler.schedulers.blocking import BlockingScheduler
# datetime: helps us log when the agent runs
from datetime import datetime
# os and sys: help Python find files in other folders
import os
import sys

# This tells Python to also look in the current folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# import our config settings
from config import POLL_INTERVAL_MINUTES

# import the main agent function
from agent import run_agent


def job():
    """This function runs every X minutes automatically."""

    # print the current time so we know when it ran
    print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — 이메일 확인 중...")

    # run the agent
    run_agent()


# this is the entry point of the program
# __name__ == "__main__" means "only run this if we run main.py directly"
if __name__ == "__main__":

    print("🚀 교수님 이메일 에이전트 시작!")
    print(f"📅 {POLL_INTERVAL_MINUTES}분마다 자동으로 이메일 확인할게요")
    print("⛔ 종료하려면 Ctrl+C 누르세요\n")

    # run once immediately when we start
    job()

    # create the scheduler
    # BlockingScheduler: keeps running until you press Ctrl+C
    scheduler = BlockingScheduler()

    # add our job to run every X minutes
    # minutes=POLL_INTERVAL_MINUTES uses the value from config.py (5 minutes)
    scheduler.add_job(job, "interval", minutes=POLL_INTERVAL_MINUTES)

    try:
        # start the scheduler — this keeps the program running forever
        scheduler.start()
    except KeyboardInterrupt:
        # when user presses Ctrl+C, shut down gracefully
        print("\n👋 에이전트 종료!")
        scheduler.shutdown()