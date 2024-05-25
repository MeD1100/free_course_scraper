from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import time
from datetime import datetime, timedelta
from email_service import send_email_notification
from utils import save_to_excel
from plyer import notification

class Scraper:
    def __init__(self, app):
        self.app = app
        self.driver = None
        self.wait = None

    def initialize_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')  # Set window size for headless mode
        options.add_argument('--start-maximized')
        options.add_argument('--enable-logging')
        options.add_argument('--log-level=0')
        options.add_argument('--ignore-certificate-errors')
        service = Service(executable_path=self.app.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def parse_release_time(self, release_time_text):
        current_time = datetime.now()
        try:
            if 'minute' in release_time_text:
                minutes = release_time_text.split()[0]
                if minutes == 'a':
                    minutes = 1
                else:
                    minutes = int(minutes)
                release_time = current_time - timedelta(minutes=minutes)
            elif 'second' in release_time_text:
                seconds = release_time_text.split()[0]
                if seconds == 'a':
                    seconds = 1
                else:
                    seconds = int(seconds)
                release_time = current_time - timedelta(seconds=seconds)
            elif 'hour' in release_time_text:
                hours = release_time_text.split()[0]
                if hours == 'an':
                    hours = 1
                else:
                    hours = int(hours)
                release_time = current_time - timedelta(hours=hours)
            elif 'day' in release_time_text:
                days = release_time_text.split()[0]
                if days == 'a':
                    days = 1
                else:
                    days = int(days)
                release_time = current_time - timedelta(days=days)
            else:
                return None
        except ValueError as e:
            self.app.log_message(f"Error parsing release time: {release_time_text}. Exception: {e}", 'error')
            notification.notify(
                title='Scraping Error',
                message=f"Error parsing release time: {release_time_text}. Exception: {e}",
                app_name='Course Scraper',
                timeout=5
            )
            return None
        return release_time

    def scrape_courses(self):
        self.initialize_driver()

        try:
            self.app.log_message("Navigating to the website...", 'header')
            url = "https://www.real.discount"
            self.driver.get(url)

            self.app.log_message("Waiting for the '100% Off' checkbox to be visible...", 'header')
            free_checkbox = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "label[for='free']")))
            self.app.log_message("'100% Off' checkbox found, attempting to click...", 'header')
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(free_checkbox).click().perform()
                self.app.log_message("Clicked the checkbox using ActionChains.", 'info')
            except Exception as e:
                self.app.log_message(f"Failed to click using ActionChains. Exception: {str(e)}", 'error')
                notification.notify(
                    title='Scraping Error',
                    message=f"Failed to click using ActionChains. Exception: {str(e)}",
                    app_name='Course Scraper',
                    timeout=5
                )

            self.app.log_message("Waiting for the page to update after clicking...", 'header')
            time.sleep(3)  # Increased sleep time

            # Select the "IT & Software" category
            self.app.log_message("Selecting the 'IT & Software' category...", 'header')
            category_dropdown = Select(self.wait.until(EC.element_to_be_clickable((By.ID, 'category'))))
            category_dropdown.select_by_visible_text('IT & Software')
            self.app.log_message("'IT & Software' category selected.", 'info')

            self.app.log_message("Waiting for the page to update after selecting category...", 'header')
            time.sleep(3)  # Increased sleep time

            scraped_links = set()  # To keep track of all scraped course links

            stop_scraping = False
            while not self.app.stop_event.is_set() and not stop_scraping:
                self.app.log_message("Extracting course information...", 'header')
                courses = self.wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'li')))
                new_courses = set()

                for course in courses:
                    if self.app.stop_event.is_set():
                        break
                    try:
                        link_element = course.find_element(By.TAG_NAME, 'a')
                        link = link_element.get_attribute('href')
                        
                        if link in scraped_links:
                            continue
                        
                        title = course.find_element(By.TAG_NAME, 'h3').text if course.find_elements(By.TAG_NAME, 'h3') else 'No Title'
                        category = course.find_element(By.TAG_NAME, 'h5').text if course.find_elements(By.TAG_NAME, 'h5') else 'No Category'
                        release_time_text = course.find_element(By.CSS_SELECTOR, 'div.col-auto.ml-0.pl-0.pr-0.mr-0').text if course.find_elements(By.CSS_SELECTOR, 'div.col-auto.ml-0.pl-0.pr-0.mr-0') else 'No Release Time'
                        if 'out-ad' in link or title == 'No Title' or link == 'No Link':
                            continue
                        release_time = self.parse_release_time(release_time_text)
                        if release_time is None:
                            continue

                        course_info = (title, category, link, release_time_text, release_time)

                        # Stop scraping if a course older than max_age_hours is found
                        max_age = datetime.now() - timedelta(hours=self.app.max_age_hours)
                        if release_time < max_age:
                            self.app.log_message(f"Found a course older than {self.app.max_age_hours} hours. Stopping scraping.", 'header')
                            stop_scraping = True
                            break

                        # Add the course link to the set of scraped links
                        scraped_links.add(link)
                        new_courses.add(course_info)
                        self.app.log_message(f"Course Title: {title}\nCategory: {category}\nLink: {link}\nRelease Time: {release_time_text}\n----------------------------------------", 'info')
                    except NoSuchElementException as e:
                        self.app.log_message("No such element found for one of the course details. Skipping this course.", 'error')
                        notification.notify(
                            title='Scraping Error',
                            message='No such element found for one of the course details. Skipping this course.',
                            app_name='Course Scraper',
                            timeout=5
                        )
                    except StaleElementReferenceException as e:
                        self.app.log_message("Stale element reference for one of the course details. Skipping this course.", 'error')
                        notification.notify(
                            title='Scraping Error',
                            message='Stale element reference for one of the course details. Skipping this course.',
                            app_name='Course Scraper',
                            timeout=5
                        )

                if stop_scraping:
                    break

                if self.app.stop_event.is_set():
                    break

                if not new_courses:
                    self.app.log_message("No new courses found or stopping condition met. Stopping.", 'header')
                    break

                self.app.all_courses.update(new_courses)

                try:
                    load_more_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.btn.btn-primary.mb-5')))
                    load_more_button.click()
                    self.app.log_message("Clicked the 'Load More' button.", 'info')
                    time.sleep(3)  # Increased sleep time
                except TimeoutException:
                    self.app.log_message("No more 'Load More' button found. All courses loaded.", 'header')
                    break
                except Exception as e:
                    self.app.log_message(f"Failed to click 'Load More' button. Exception: {str(e)}", 'error')
                    notification.notify(
                        title='Scraping Error',
                        message=f"Failed to click 'Load More' button. Exception: {str(e)}",
                        app_name='Course Scraper',
                        timeout=5
                    )
                    break

        except TimeoutException as e:
            self.app.log_message(f"Timeout while waiting for an element. Exception: {str(e)}", 'error')
            notification.notify(
                title='Scraping Error',
                message=f"Timeout while waiting for an element. Exception: {str(e)}",
                app_name='Course Scraper',
                timeout=5
            )
        except Exception as e:
            self.app.log_message(f"An error occurred: {str(e)}", 'error')
            notification.notify(
                title='Scraping Error',
                message=f"An error occurred: {str(e)}",
                app_name='Course Scraper',
                timeout=5
            )
        finally:
            if self.app.all_courses:
                sorted_courses = sorted(self.app.all_courses, key=lambda x: x[4])
                save_to_excel(sorted_courses, self.app.save_location)
                self.app.log_message("Scraping completed and data saved to Excel.", 'header')
                try:
                    send_email_notification(self.app.email_address, sorted_courses)
                    self.app.log_message("Email notification sent successfully.", 'info')
                    self.app.stop_event.set()  # Stop scraping after sending the email
                    notification.notify(
                        title='Scraping Completed',
                        message='The scraping process has completed successfully.',
                        app_name='Course Scraper',
                        timeout=5
                    )
                except Exception as e:
                    self.app.log_message(f"Failed to send email notification. Exception: {str(e)}", 'error')
                    notification.notify(
                        title='Email Error',
                        message=f"Failed to send email notification. Exception: {str(e)}",
                        app_name='Course Scraper',
                        timeout=5
                    )
            self.driver.quit()