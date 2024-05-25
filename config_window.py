import tkinter as tk
from tkinter import filedialog

class ConfigWindow:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.root.title("Configuration")
        self.root.geometry('400x300')
        self.root.configure(bg='#2e2e2e')

        tk.Label(root, text="Max Age Hours", bg='#2e2e2e', fg='white', font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.max_age_var = tk.StringVar(value=str(app.max_age_hours))
        self.max_age_dropdown = tk.OptionMenu(root, self.max_age_var, *[str(i) for i in range(1, 25)])
        self.max_age_dropdown.config(bg='#1e1e1e', fg='white', font=('Arial', 12))
        self.max_age_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

        tk.Label(root, text="Save Location", bg='#2e2e2e', fg='white', font=('Arial', 12)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.save_location_var = tk.StringVar(value=app.save_location if app.save_location else "")
        tk.Entry(root, textvariable=self.save_location_var, bg='#1e1e1e', fg='white', font=('Arial', 12)).grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        tk.Button(root, text="Browse", command=self.browse_save_location, bg='#2196f3', fg='white', font=('Arial', 12)).grid(row=1, column=2, padx=10, pady=10, sticky='ew')

        tk.Label(root, text="Recipient Email", bg='#2e2e2e', fg='white', font=('Arial', 12)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        self.email_var = tk.StringVar(value=app.email_address)
        tk.Entry(root, textvariable=self.email_var, bg='#1e1e1e', fg='white', font=('Arial', 12)).grid(row=2, column=1, padx=10, pady=10, sticky='ew')

        tk.Label(root, text="Category", bg='#2e2e2e', fg='white', font=('Arial', 12)).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.category_var = tk.StringVar(value='IT & Software')
        category_entry = tk.Entry(root, textvariable=self.category_var, bg='#1e1e1e', fg='white', font=('Arial', 12), state='disabled')
        category_entry.grid(row=3, column=1, padx=10, pady=10, sticky='ew')
        category_entry.bind("<Enter>", lambda e: category_entry.config(cursor="no"))

        tk.Button(root, text="Save", command=self.save_config, bg='#4caf50', fg='white', font=('Arial', 12)).grid(row=4, column=0, columnspan=3, pady=20, padx=10, sticky='ew')

        root.grid_columnconfigure(1, weight=1)

    def browse_save_location(self):
        save_location = filedialog.askdirectory()
        if save_location:
            self.save_location_var.set(save_location)

    def save_config(self):
        try:
            self.app.max_age_hours = int(self.max_age_var.get())
            self.app.save_location = self.save_location_var.get()
            self.app.email_address = self.email_var.get()

            # Ensure the 'Settings' section exists
            if not self.app.config.has_section('Settings'):
                self.app.config.add_section('Settings')
            
            # Save to config file
            self.app.config.set('Settings', 'max_age_hours', str(self.app.max_age_hours))
            self.app.config.set('Settings', 'save_location', self.app.save_location)
            self.app.config.set('Settings', 'email_address', self.app.email_address)
            
            with open('config.ini', 'w') as configfile:
                self.app.config.write(configfile)
            
            self.root.destroy()
            self.app.log_message("Configuration saved.", 'info')
        except ValueError:
            self.app.log_message("Invalid value for max age hours. Please enter a number.", 'error')