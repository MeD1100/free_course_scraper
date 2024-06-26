import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread, Event
import os
from datetime import datetime
import configparser
from config_window import ConfigWindow
from instructions_window import InstructionsWindow
from scraper import Scraper
from utils import save_to_excel
from plyer import notification
from scheduler import ScraperScheduler

class NewsScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Course Scraper")
        self.center_window(800, 500)  # Adjusted height to 500 pixels
        self.root.configure(bg='#2e2e2e')

        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.driver_path = self.config.get('Paths', 'driver_path')
        self.max_age_minutes = self.config.getint('Settings', 'max_age_minutes', fallback=120)  # Default to 120 minutes
        self.save_location = self.config.get('Settings', 'save_location', fallback=os.getcwd())
        self.email_address = self.config.get('Settings', 'email_address', fallback="")

        self.log = scrolledtext.ScrolledText(root, state='disabled', height=15, width=80, bg='#1e1e1e', fg='white', font=('Arial', 12), insertbackground='white')
        self.log.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        self.progress = ttk.Progressbar(root, orient="horizontal", length=100, mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky='ew')

        self.start_button = ttk.Button(root, text="Start Scraping", command=self.start_scraping)
        self.start_button.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
        self.stop_button = ttk.Button(root, text="Stop Scraping", command=self.stop_scraping, state='disabled')
        self.stop_button.grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        self.config_button = ttk.Button(root, text="Config", command=self.open_config)
        self.config_button.grid(row=2, column=2, sticky='ew', padx=10, pady=5)

        self.schedule_start_button = ttk.Button(root, text="Start Schedule", command=self.start_schedule)
        self.schedule_start_button.grid(row=3, column=0, sticky='ew', padx=10, pady=5)
        self.schedule_stop_button = ttk.Button(root, text="Stop Schedule", command=self.stop_schedule, state='disabled')
        self.schedule_stop_button.grid(row=3, column=1, sticky='ew', padx=10, pady=5)
        self.schedule_status_button = ttk.Button(root, text="Schedule Status", command=self.show_schedule_status)
        self.schedule_status_button.grid(row=3, column=2, sticky='ew', padx=10, pady=5)

        self.instructions_button = ttk.Button(root, text="Instructions", command=self.show_instructions)
        self.instructions_button.grid(row=4, column=0, columnspan=3, sticky='ew', padx=10, pady=10)

        self.stop_event = Event()
        self.scraper_thread = None
        self.all_courses = set()
        self.scheduler = ScraperScheduler(self)

        self.update_schedule_buttons()

        # Configure grid weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def log_message(self, message, tag=None):
        self.log.configure(state='normal')
        self.log.insert(tk.END, message + "\n", tag)
        self.log.configure(state='disabled')
        self.log.yview(tk.END)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

    def start_scraping(self):
        self.stop_event.clear()
        self.progress['value'] = 0
        self.scraper_thread = Thread(target=self.scrape_courses)
        self.scraper_thread.start()
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.config_button.config(state='disabled')
        self.log_message("Started scraping.", 'header')
        notification.notify(
            title='Scraping Started',
            message='The scraping process has started.',
            app_name='Course Scraper',
            timeout=5
        )

    def stop_scraping(self):
        self.stop_event.set()
        if self.scraper_thread.is_alive():
            self.scraper_thread.join()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.config_button.config(state='normal')
        self.log_message("Stopped scraping.", 'header')
        notification.notify(
            title='Scraping Stopped',
            message='The scraping process has been stopped.',
            app_name='Course Scraper',
            timeout=5
        )

    def open_config(self):
        config_window = tk.Toplevel(self.root)
        config_window.grab_set()
        ConfigWindow(config_window, self)

    def start_schedule(self):
        interval_minutes = self.max_age_minutes  # Adjust this as needed
        self.scheduler.start(interval_minutes / 60.0)  # Convert to hours for scheduler
        self.update_schedule_buttons()

    def stop_schedule(self):
        self.scheduler.stop()
        self.update_schedule_buttons()

    def show_schedule_status(self):
        status = self.scheduler.status()
        self.log_message(status, 'info')


    def show_instructions(self):
        instructions_window = tk.Toplevel(self.root)
        instructions_window.grab_set()
        InstructionsWindow(instructions_window, self)

    def update_schedule_buttons(self):
        if self.scheduler.is_running():
            self.schedule_start_button.config(state='disabled')
            self.schedule_stop_button.config(state='normal')
        else:
            self.schedule_start_button.config(state='normal')
            self.schedule_stop_button.config(state='disabled')

    def scrape_courses(self):
        scraper = Scraper(self)
        scraper.scrape_courses()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.config_button.config(state='normal')
        self.progress['value'] = 100
        self.log_message("Progress: 100% completed.", 'header')
        self.root.after(2000, self.reset_progress)  # Reset progress bar after 2 seconds
        notification.notify(
            title='Scraping Completed',
            message='The scraping process has completed successfully.',
            app_name='Course Scraper',
            timeout=5
        )

    def reset_progress(self):
        self.progress['value'] = 0

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

def main():
    root = tk.Tk()

    app = NewsScraperApp(root)

    # Add custom tags for colored text
    app.log.tag_config('header', foreground='#FFD700')
    app.log.tag_config('info', foreground='#00FF00')
    app.log.tag_config('error', foreground='#FF0000')

    root.mainloop()

if __name__ == "__main__":
    main()