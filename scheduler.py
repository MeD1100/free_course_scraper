from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

class ScraperScheduler:
    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.job = None

    def start(self, interval_hours):
        if self.job:
            self.scheduler.remove_job(self.job.id)
        self.job = self.scheduler.add_job(self.app.start_scraping, trigger=IntervalTrigger(hours=interval_hours), next_run_time=datetime.now())
        self.scheduler.start()
        self.app.log_message(f"Scheduler started to run every {interval_hours} hour(s).", 'info')

    def stop(self):
        if self.job:
            self.scheduler.remove_job(self.job.id)
            self.job = None
        self.scheduler.shutdown()
        self.app.log_message("Scheduler stopped.", 'info')
