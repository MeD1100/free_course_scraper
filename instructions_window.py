import tkinter as tk
from tkinter import ttk

class InstructionsWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.root.title("Instructions")
        self.center_window(600, 600)  # Adjusted height to 500 pixels
        self.root.configure(bg='#2e2e2e')

        instructions_frame = tk.Frame(self.root, bg='#2e2e2e')
        instructions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        instructions = (
            "Course Scraper Instructions:\n\n"
            "1. Configuration:\n"
            "   - Click 'Config' to open the configuration window.\n"
            "   - Set the maximum age for courses in hours (2 to 24).\n"
            "   - Choose the location to save the Excel file.\n"
            "   - Enter the recipient email address for notifications.\n"
            "   - Save the configuration.\n\n"
            "2. Start Scraping:\n"
            "   - Click 'Start Scraping' to begin the scraping process.\n"
            "   - The progress bar will indicate the scraping progress.\n"
            "   - Scraping logs will appear in the main window.\n"
            "   - An email notification will be sent upon completion.\n\n"
            "3. Stop Scraping:\n"
            "   - Click 'Stop Scraping' to halt the scraping process.\n\n"
            "4. Scheduling:\n"
            "   - Click 'Start Schedule' to start automatic scraping at intervals based on max age.\n"
            "   - Click 'Stop Schedule' to stop the scheduled scraping.\n"
            "   - Click 'Schedule Status' to view the current schedule status.\n\n"
            "5. Instructions:\n"
            "   - Click 'Instructions' to view these instructions at any time."
        )

        instructions_text = tk.Text(instructions_frame, wrap=tk.WORD, bg='#2e2e2e', fg='white', font=('Arial', 12), relief=tk.FLAT)
        instructions_text.insert(tk.END, instructions)
        instructions_text.config(state=tk.DISABLED)  # Make the text read-only
        instructions_text.pack(fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(self.root, bg='#2e2e2e')
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.ok_button = ttk.Button(button_frame, text="OK", command=self.root.destroy)
        self.ok_button.pack(pady=10, ipadx=10, ipady=5)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
