import tkinter as tk
from tkinter import ttk, filedialog

class ConfigWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.root.title("Configuration")
        self.center_window(600, 300)  # Adjusted width to 600 pixels
        self.root.configure(bg='#2e2e2e')

        tk.Label(root, text="Max Age (hours)", bg='#2e2e2e', fg='white', font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=10, sticky='w')

        self.max_age_var = tk.IntVar(value=self.app.max_age_minutes // 60)  # Convert minutes to hours
        self.max_age_slider = ttk.Scale(root, from_=2, to=24, orient=tk.HORIZONTAL, variable=self.max_age_var, length=300, command=self.update_max_age_label)
        self.max_age_slider.grid(row=0, column=1, padx=10, pady=10, sticky='ew', columnspan=2)

        self.max_age_label = tk.Label(root, text=f"{self.app.max_age_minutes // 60} hours", bg='#2e2e2e', fg='white', font=('Arial', 12))
        self.max_age_label.grid(row=0, column=3, padx=10, pady=10, sticky='w')

        tk.Label(root, text="Save Location", bg='#2e2e2e', fg='white', font=('Arial', 12)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.save_location_var = tk.StringVar(value=self.app.save_location if self.app.save_location else "")
        tk.Entry(root, textvariable=self.save_location_var, bg='#1e1e1e', fg='white', font=('Arial', 12)).grid(row=1, column=1, padx=10, pady=10, sticky='ew', columnspan=2)
        tk.Button(root, text="Browse", command=self.browse_save_location, bg='#2196f3', fg='white', font=('Arial', 12)).grid(row=1, column=3, padx=10, pady=10, sticky='ew')

        tk.Label(root, text="Recipient Email", bg='#2e2e2e', fg='white', font=('Arial', 12)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.email_var = tk.StringVar(value=self.app.email_address)
        tk.Entry(root, textvariable=self.email_var, bg='#1e1e1e', fg='white', font=('Arial', 12)).grid(row=2, column=1, padx=10, pady=10, sticky='ew', columnspan=3)

        tk.Label(root, text="Category", bg='#2e2e2e', fg='white', font=('Arial', 12)).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.category_var = tk.StringVar(value='IT & Software')
        category_entry = tk.Entry(root, textvariable=self.category_var, bg='#1e1e1e', fg='white', font=('Arial', 12), state='disabled')
        category_entry.grid(row=3, column=1, padx=10, pady=10, sticky='ew', columnspan=3)
        category_entry.bind("<Enter>", lambda e: category_entry.config(cursor="no"))

        tk.Button(root, text="Save", command=self.save_config, bg='#4caf50', fg='white', font=('Arial', 12)).grid(row=4, column=0, columnspan=4, pady=20, padx=10, sticky='ew')

        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry(f'{width}x{height}+{int(x)}+{int(y)}')

    def update_max_age_label(self, event):
        value = self.max_age_var.get()
        self.max_age_label.config(text=f"{value} hours")

    def browse_save_location(self):
        save_location = filedialog.askdirectory()
        if save_location:
            self.save_location_var.set(save_location)

    def save_config(self):
        try:
            self.app.max_age_minutes = self.max_age_var.get() * 60  # Convert hours to minutes
            self.app.save_location = self.save_location_var.get()
            self.app.email_address = self.email_var.get()

            # Ensure the 'Settings' section exists
            if not self.app.config.has_section('Settings'):
                self.app.config.add_section('Settings')

            # Save to config file
            self.app.config.set('Settings', 'max_age_minutes', str(self.app.max_age_minutes))
            self.app.config.set('Settings', 'save_location', self.app.save_location)
            self.app.config.set('Settings', 'email_address', self.app.email_address)

            with open('config.ini', 'w') as configfile:
                self.app.config.write(configfile)

            self.root.destroy()
            self.app.log_message("Configuration saved.", 'info')
        except ValueError:
            self.app.log_message("Invalid value for max age. Please enter a number.", 'error')