import tkinter as tk
from tkinter import scrolledtext
from threading import Thread, Event
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import os
from datetime import datetime, timedelta
import openpyxl

class NewsScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Course Scraper")
        self.center_window(800, 600)
        self.root.configure(bg='#1c1c1c')

        self.save_location = os.getcwd()
        self.category = 'IT & Software'
        self.max_age_hours = 24  # Default to 24 hours

        customFont = ('Consolas', 12)
        self.log = scrolledtext.ScrolledText(root, font=customFont, fg='#D8DEE9', bg='#2e2e2e', wrap=tk.WORD, padx=10, pady=10)
        self.log.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        buttonStyle = {'font': customFont, 'bg': '#5E81AC', 'fg': '#ECEFF4', 'padx': 10, 'pady': 5, 'relief': 'raised', 'bd': 3}
        self.start_button = tk.Button(root, text="Start Scraping", command=self.start_scraping, **buttonStyle)
        self.start_button.grid(row=1, column=0, sticky='ew', padx=10, pady=10)
        self.stop_button = tk.Button(root, text="Stop Scraping", command=self.stop_scraping, state='disabled', **buttonStyle)
        self.stop_button.grid(row=1, column=1, sticky='ew', padx=10, pady=10)
        self.config_button = tk.Button(root, text="Config", command=self.open_config, **buttonStyle)
        self.config_button.grid(row=1, column=2, sticky='ew', padx=10, pady=10)

        self.running = False
        self.stop_event = Event()
        self.driver = None
        self.all_courses = []  # Track all scraped courses

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def open_config(self):
        config_root = tk.Toplevel(self.root)
        config_window = ConfigWindow(config_root, self)

    def log_message(self, message, color='info'):
        tag = color
        self.log.configure(state='normal')
        self.log.insert(tk.END, message + "\n", tag)
        self.log.configure(state='disabled')
        self.log.yview(tk.END)

    def initialize_driver(self):
        driver_path = r'C:\Mohamed\Personal-apps\Discount-courses-udemy-desktop-app\chromedriver_win64\chromedriver-win64\chromedriver.exe'
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')  # Set window size for headless mode
        options.add_argument('--start-maximized')
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=0')
        options.add_argument('--ignore-certificate-errors')
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def is_course_older_than_max_hours(self, release_time_text, max_age_seconds):
        current_time = datetime.now()
        try:
            if 'minute' in release_time_text:
                minutes = int(release_time_text.split()[0])
                release_time = current_time - timedelta(minutes=minutes)
            elif 'hour' in release_time_text:
                hours = release_time_text.split()[0]
                if hours == 'an':
                    hours = 1
                else:
                    hours = int(hours)
                release_time = current_time - timedelta(hours=hours)
            elif 'day' in release_time_text:
                days = int(release_time_text.split()[0])
                release_time = current_time - timedelta(days=days)
            else:
                return False  # If no recognizable time format, consider it not older
        except ValueError as e:
            self.log_message(f"Error parsing release time: {release_time_text}. Exception: {e}", 'error')
            return False

        return (current_time - release_time).total_seconds() > max_age_seconds

    def scrape_courses(self):
        self.initialize_driver()

        try:
            self.log_message("Navigating to the website...", 'header')
            url = "https://www.real.discount"
            self.driver.get(url)

            self.log_message("Waiting for the '100% Off' checkbox to be visible...", 'header')
            free_checkbox = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "label[for='free']")))
            self.log_message("'100% Off' checkbox found, attempting to click...", 'header')
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(free_checkbox).click().perform()
                self.log_message("Clicked the checkbox using ActionChains.", 'info')
            except Exception as e:
                self.log_message(f"Failed to click using ActionChains. Exception: {str(e)}", 'error')

            self.log_message("Waiting for the page to update after clicking...", 'header')
            time.sleep(3)  # Increased sleep time

            # Select the "IT & Software" category
            self.log_message("Selecting the 'IT & Software' category...", 'header')
            category_dropdown = Select(self.wait.until(EC.element_to_be_clickable((By.ID, 'category'))))
            category_dropdown.select_by_visible_text('IT & Software')
            self.log_message("'IT & Software' category selected.", 'info')

            self.log_message("Waiting for the page to update after selecting category...", 'header')
            time.sleep(3)  # Increased sleep time

            self.all_courses = set()  # To keep track of all scraped courses and avoid duplicates

            while True:
                self.log_message("Extracting course information...", 'header')
                courses = self.wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'li')))
                new_courses = set()

                for course in courses:
                    try:
                        title = course.find_element(By.TAG_NAME, 'h3').text if course.find_elements(By.TAG_NAME, 'h3') else 'No Title'
                        category = course.find_element(By.TAG_NAME, 'h5').text if course.find_elements(By.TAG_NAME, 'h5') else 'No Category'
                        link = course.find_element(By.TAG_NAME, 'a').get_attribute('href') if course.find_elements(By.TAG_NAME, 'a') else 'No Link'
                        release_time = course.find_element(By.CSS_SELECTOR, 'div.col-auto.ml-0.pl-0.pr-0.mr-0').text if course.find_elements(By.CSS_SELECTOR, 'div.col-auto.ml-0.pl-0.pr-0.mr-0') else 'No Release Time'
                        if 'out-ad' in link or title == 'No Title' or link == 'No Link':
                            continue
                        course_info = (title, category, link, release_time)

                        max_age_seconds = self.max_age_hours * 3600
                        if self.is_course_older_than_max_hours(release_time, max_age_seconds):
                            self.log_message("Course older than the max hours found. Stopping scraping.", 'header')
                            break

                        if course_info not in self.all_courses:
                            self.all_courses.add(course_info)
                            new_courses.add(course_info)
                            self.log_message(f"Course Title: {title}\nCategory: {category}\nLink: {link}\nRelease Time: {release_time}\n----------------------------------------", 'info')
                    except (NoSuchElementException, StaleElementReferenceException):
                        self.log_message("No such element found for one of the course details. Skipping this course.", 'error')

                else:
                    # Continue only if no break was encountered
                    try:
                        load_more_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.btn.btn-primary.mb-5')))
                        load_more_button.click()
                        self.log_message("Clicked the 'Load More' button.", 'info')
                        time.sleep(3)  # Increased sleep time
                        continue
                    except TimeoutException:
                        self.log_message("No more 'Load More' button found. All courses loaded.", 'header')
                    except Exception as e:
                        self.log_message(f"Failed to click 'Load More' button. Exception: {str(e)}", 'error')

                break  # Break the outer while loop if a break was encountered in the for loop

        except TimeoutException as e:
            self.log_message(f"Timeout while waiting for an element. Exception: {str(e)}", 'error')
        except Exception as e:
            self.log_message(f"An error occurred: {str(e)}", 'error')
        finally:
            self.save_to_excel(self.all_courses)
            self.driver.quit()


    def start_scraping(self):
        self.running = True
        self.stop_event.clear()
        self.thread = Thread(target=self.scrape_courses)
        self.thread.start()
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.config_button.config(state='disabled')
        self.log_message("Started scraping.", 'header')

    def stop_scraping(self):
        self.running = False
        self.stop_event.set()
        if self.thread.is_alive():
            self.thread.join()
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.config_button.config(state='normal')
        self.log_message("Stopped scraping.", 'header')

    def save_to_excel(self, courses):
        today_date = datetime.now().strftime("%d%m%Y")
        file_name = os.path.join(self.save_location, f"free_courses_{today_date}.xlsx")
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Scraped Courses"
        headers = ["Course Title", "Category", "Link", "Release Time"]
        sheet.append(headers)

        for course in courses:
            sheet.append(course)

        # Adjust column widths
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column name
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column].width = adjusted_width

        try:
            workbook.save(file_name)
            self.log_message(f"Saved scraped data to {file_name}", 'info')
        except Exception as e:
            self.log_message(f"Error saving to Excel file: {str(e)}", 'error')


    def on_closing(self):
        if self.running:
            self.stop_scraping()
        self.root.destroy()

class ConfigWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.root.title("Configuration")
        self.center_window(400, 300)
        self.root.configure(bg='#1c1c1c')

        customFont = ('Consolas', 12)

        self.label_save_location = tk.Label(root, text="Save Location:", font=customFont, fg='#D8DEE9', bg='#1c1c1c')
        self.label_save_location.pack(pady=5)
        self.entry_save_location = tk.Entry(root, font=customFont, fg='#D8DEE9', bg='#2e2e2e')
        self.entry_save_location.insert(0, self.app.save_location)
        self.entry_save_location.pack(pady=5)

        self.label_category = tk.Label(root, text="Category:", font=customFont, fg='#D8DEE9', bg='#1c1c1c')
        self.label_category.pack(pady=5)
        self.entry_category = tk.Entry(root, font=customFont, fg='#D8DEE9', bg='#2e2e2e', state='normal')
        self.entry_category.insert(0, self.app.category)
        self.entry_category.configure(state='disabled', disabledbackground='#4c4c4c', disabledforeground='#D8DEE9', cursor='X_cursor')
        self.entry_category.pack(pady=5)

        self.label_max_age = tk.Label(root, text="Max Age (hours):", font=customFont, fg='#D8DEE9', bg='#1c1c1c')
        self.label_max_age.pack(pady=5)
        self.entry_max_age = tk.Entry(root, font=customFont, fg='#D8DEE9', bg='#2e2e2e')
        self.entry_max_age.insert(0, self.app.max_age_hours)
        self.entry_max_age.pack(pady=5)

        self.save_button = tk.Button(root, text="Save", command=self.save_config, font=customFont, bg='#5E81AC', fg='#ECEFF4', relief='raised', bd=3)
        self.save_button.pack(pady=5)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def save_config(self):
        self.app.save_location = self.entry_save_location.get()
        self.app.max_age_hours = int(self.entry_max_age.get())
        self.app.log_message(f"Configuration saved: Save Location - {self.app.save_location}, Max Age - {self.app.max_age_hours} hours", 'info')
        self.root.destroy()


def main():
    root = tk.Tk()
    app = NewsScraperApp(root)
    
    # Add custom tags for colored text
    app.log.tag_config('header', foreground='#88C0D0')
    app.log.tag_config('info', foreground='#A3BE8C')
    app.log.tag_config('error', foreground='#BF616A')
    app.log.tag_config('warning', foreground='#EBCB8B')

    root.mainloop()

if __name__ == "__main__":
    main()
