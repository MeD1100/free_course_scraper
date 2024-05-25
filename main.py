import tkinter as tk
from tkinter import scrolledtext
from threading import Thread, Event
import os
from datetime import datetime
import configparser
from config_window import ConfigWindow
from scraper import Scraper
from utils import save_to_excel

class NewsScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Course Scraper")
        self.root.geometry('800x600')
        self.root.configure(bg='#2e2e2e')

        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.driver_path = self.config.get('Paths', 'driver_path')

        self.log = scrolledtext.ScrolledText(root, state='disabled', height=20, width=80, bg='#1e1e1e', fg='white', font=('Arial', 12), insertbackground='white')
        self.log.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        self.start_button = tk.Button(root, text="Start Scraping", command=self.start_scraping, bg='#4caf50', fg='white', font=('Arial', 12))
        self.start_button.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        self.stop_button = tk.Button(root, text="Stop Scraping", command=self.stop_scraping, state='disabled', bg='#f44336', fg='white', font=('Arial', 12))
        self.stop_button.grid(row=1, column=1, sticky='ew', padx=10, pady=10)
        self.config_button = tk.Button(root, text="Config", command=self.open_config, bg='#2196f3', fg='white', font=('Arial', 12))
        self.config_button.grid(row=1, column=2, sticky='ew', padx=10, pady=10)

        self.stop_event = Event()
        self.scraper_thread = None
        self.all_courses = set()
        self.max_age_hours = 24
        self.save_location = os.getcwd()
        self.email_address = ""

    def log_message(self, message, tag=None):
        self.log.configure(state='normal')
        self.log.insert(tk.END, message + "\n", tag)
        self.log.configure(state='disabled')
        self.log.yview(tk.END)

    def start_scraping(self):
        self.stop_event.clear()
        self.scraper_thread = Thread(target=self.scrape_courses)
        self.scraper_thread.start()
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.config_button.config(state='disabled')
        self.log_message("Started scraping.", 'header')

    def stop_scraping(self):
        self.stop_event.set()
        self.scraper_thread.join()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.config_button.config(state='normal')
        self.log_message("Stopped scraping.", 'header')

    def open_config(self):
        config_window = tk.Toplevel(self.root)
        config_window.grab_set()
        ConfigWindow(config_window, self)

    def scrape_courses(self):
        scraper = Scraper(self)
        scraper.scrape_courses()

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