import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

def view_database():
    conn = sqlite3.connect('shipping_db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    records = cursor.fetchall()
    conn.close()
    display_records(records)

def display_records(records):
    # Clear existing items in the treeview
    for item in tree.get_children():
        tree.delete(item)
    
    # Insert new records
    for record in records:
        tree.insert('', 'end', values=record)

def initialize_database():
    conn = sqlite3.connect('shipping_db.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS customers")
    cursor.execute('''
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        shipping_statement TEXT
    )
    ''')
    
    customers = [
        ("customer1@email.com", "Customer 1 requires express shipping for all orders. Package must be double-boxed for extra protection. Signature required upon delivery. Please include a personalized thank-you note with each shipment."),
        ("customer2@email.com", "Customer 2 prefers eco-friendly packaging. Use recycled materials whenever possible. Delivery instructions: Leave packages at the side door. No signature required for orders under $500."),
        ("customer3@email.com", "Customer 3 has a corporate account. Bulk shipments only. Palletize orders exceeding 20 items. Provide tracking information via email and SMS. Delivery window: Monday to Friday, 9 AM to 5 PM only.")
    ]
    
    for email, statement in customers:
        cursor.execute('''
        INSERT OR IGNORE INTO customers (name, email, shipping_statement)
        VALUES (?, ?, ?)
        ''', (email.split('@')[0], email, statement))
    
    conn.commit()
    conn.close()
    messagebox.showinfo("Initialization", "Database has been re-initialized.")
    view_database()  # Refresh the view after initialization

def on_double_click(event):
    item = tree.selection()[0]
    values = tree.item(item, "values")
    show_details(values)

def show_details(values):
    details_window = tk.Toplevel(root)
    details_window.title(f"Details for {values[1]}")
    details_window.geometry("400x300")
    
    tk.Label(details_window, text=f"ID: {values[0]}").pack(anchor="w", padx=10, pady=5)
    tk.Label(details_window, text=f"Name: {values[1]}").pack(anchor="w", padx=10, pady=5)
    tk.Label(details_window, text=f"Email: {values[2]}").pack(anchor="w", padx=10, pady=5)
    
    tk.Label(details_window, text="Shipping Statement:").pack(anchor="w", padx=10, pady=5)
    statement_text = tk.Text(details_window, wrap=tk.WORD, width=45, height=8)
    statement_text.insert(tk.END, values[3])
    statement_text.config(state=tk.DISABLED)
    statement_text.pack(padx=10, pady=5)

root = tk.Tk()
root.title("Shipping Database Manager")
root.geometry("800x600")

# Create a frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

view_btn = tk.Button(button_frame, text="Refresh Database View", command=view_database)
view_btn.pack(side=tk.LEFT, padx=5)

init_btn = tk.Button(button_frame, text="Initialize Database", command=initialize_database)
init_btn.pack(side=tk.LEFT, padx=5)

# Create Treeview
tree = ttk.Treeview(root, columns=("ID", "Name", "Email", "Shipping Statement"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Email", text="Email")
tree.heading("Shipping Statement", text="Shipping Statement")

tree.column("ID", width=50)
tree.column("Name", width=100)
tree.column("Email", width=200)
tree.column("Shipping Statement", width=400)

tree.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

# Bind double-click event
tree.bind("<Double-1>", on_double_click)

# Add scrollbar
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Initialize the view
view_database()

root.mainloop()