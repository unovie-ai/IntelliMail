import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re

class DatabaseManagerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Database Manager")
        self.root.geometry("800x600")
        
        # Create main container
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize button
        self.init_button = ttk.Button(
            self.main_frame, 
            text="Initialize Database", 
            command=self.initialize_database
        )
        self.init_button.grid(row=0, column=0, pady=10, sticky=tk.W)
        
        # Refresh button
        self.refresh_button = ttk.Button(
            self.main_frame, 
            text="Refresh View", 
            command=self.refresh_view
        )
        self.refresh_button.grid(row=0, column=1, pady=10, padx=10, sticky=tk.W)
        
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Customers tab
        self.customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_frame, text="Customers")
        
        # Email History tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Email History")
        
        # Set up the customers treeview
        self.setup_customers_view()
        
        # Set up the email history treeview
        self.setup_history_view()
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

    def setup_customers_view(self):
        # Create Treeview
        columns = ('ID', 'Name', 'Email', 'Phone', 'Title', 'Company', 
                  'Last Contact', 'Billing Issues', 'Shipping Issues', 'Other Issues')
        self.customers_tree = ttk.Treeview(self.customers_frame, columns=columns, show='headings')
        
        # Set column headings
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=100)  # Adjust width as needed
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(self.customers_frame, orient=tk.VERTICAL, command=self.customers_tree.yview)
        x_scroll = ttk.Scrollbar(self.customers_frame, orient=tk.HORIZONTAL, command=self.customers_tree.xview)
        self.customers_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid layout
        self.customers_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        y_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        x_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.customers_frame.columnconfigure(0, weight=1)
        self.customers_frame.rowconfigure(0, weight=1)

    def setup_history_view(self):
        # Create Treeview
        columns = ('ID', 'Customer ID', 'Email Content', 'Issue Type', 'Sent Date')
        self.history_tree = ttk.Treeview(self.history_frame, columns=columns, show='headings')
        
        # Set column headings
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        # Set larger width for Email Content
        self.history_tree.column('Email Content', width=300)
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        x_scroll = ttk.Scrollbar(self.history_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid layout
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        y_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        x_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.history_frame.columnconfigure(0, weight=1)
        self.history_frame.rowconfigure(0, weight=1)

    def initialize_database(self):
        try:
            # Connect to SQLite database
            conn = sqlite3.connect('db_for_classification.sqlite')
            cursor = conn.cursor()
            
            # Drop existing tables
            cursor.execute('DROP TABLE IF EXISTS email_history')
            cursor.execute('DROP TABLE IF EXISTS customers')
            
            # Create customers table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                title TEXT,
                company TEXT,
                last_contact_date TEXT,
                last_email_content TEXT,
                billing_issues_count INTEGER DEFAULT 0,
                shipping_issues_count INTEGER DEFAULT 0,
                other_issues_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create email_history table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_history (
                email_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                email_content TEXT,
                issue_type TEXT,
                sent_date TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
            ''')
            
            # Insert test data
            test_customers = [
                ('Customer One', 'customer1@email.com', '123-456-7890', 'Manager', 'ABC Corp',
                 datetime.datetime.now().isoformat(), 'Previous email content about billing...', 2, 1, 0),
                ('Customer Two', 'customer2@email.com', '234-567-8901', 'Director', 'XYZ Ltd',
                 datetime.datetime.now().isoformat(), 'Previous email content about shipping...', 0, 3, 1),
                ('Customer Three', 'customer3@email.com', '345-678-9012', 'CEO', '123 Industries',
                 datetime.datetime.now().isoformat(), 'Previous email content about other issues...', 1, 0, 2)
            ]
            
            cursor.executemany('''
            INSERT OR IGNORE INTO customers 
            (name, email, phone, title, company, last_contact_date, last_email_content,
             billing_issues_count, shipping_issues_count, other_issues_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', test_customers)
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Database initialized successfully!")
            self.refresh_view()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize database: {str(e)}")

    def refresh_view(self):
        try:
            conn = sqlite3.connect('db_for_classification.sqlite')
            cursor = conn.cursor()
            
            # Clear existing items
            for item in self.customers_tree.get_children():
                self.customers_tree.delete(item)
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Fetch and display customers
            cursor.execute('''
                SELECT customer_id, name, email, phone, title, company, 
                       last_contact_date, billing_issues_count, 
                       shipping_issues_count, other_issues_count 
                FROM customers
            ''')
            for row in cursor.fetchall():
                self.customers_tree.insert('', tk.END, values=row)
            
            # Fetch and display email history
            cursor.execute('SELECT * FROM email_history')
            for row in cursor.fetchall():
                self.history_tree.insert('', tk.END, values=row)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh view: {str(e)}")

def main():
    root = tk.Tk()
    app = DatabaseManagerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()