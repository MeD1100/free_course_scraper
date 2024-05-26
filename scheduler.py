from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta

class ScraperScheduler:
    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.job = None

    def start(self, interval_hours):
        if self.job:
            self.scheduler.remove_job(self.job.id)
        self.job = self.scheduler.add_job(self.app.start_scraping, trigger=IntervalTrigger(hours=interval_hours), next_run_time=datetime.now(), id='scrape_job')
        self.scheduler.start()
        self.app.log_message(f"Scheduler started to run every {interval_hours} hour(s). Next run at {datetime.now() + timedelta(hours=interval_hours)}.", 'info')

    def stop(self):
        if self.job:
            self.scheduler.remove_job(self.job.id)
            self.job = None
        self.scheduler.shutdown()
        self.app.log_message("Scheduler stopped.", 'info')

    def status(self):
        jobs = self.scheduler.get_jobs()
        return f"Scheduler running: {self.scheduler.running}\nJobs: {jobs}"

    def is_running(self):
        return self.scheduler.running and self.job is not None
