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
        if self.scheduler.running and self.job:
            next_run_time = self.job.next_run_time.replace(tzinfo=None)  # Convert to naive datetime
            remaining_time = next_run_time - datetime.now()
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_remaining_time = f"{hours} hours, {minutes} minutes, and {seconds} seconds"
            return (f"Scheduler running: True\n"
                    f"Next run in: {formatted_remaining_time}\n"
                    f"Job: {self.job.name} (ID: {self.job.id})")
        return f"Scheduler running: {self.scheduler.running}\nNo jobs currently scheduled."

    def is_running(self):
        return self.scheduler.running and self.job is not None
