import sqlite3
from datetime import datetime, timedelta

def initialize_database():
    """Initialize or reset the billing database."""
    conn = sqlite3.connect('billing_db.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS billing_customers")
    cursor.execute('''
    CREATE TABLE billing_customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        billing_statement TEXT
    )
    ''')

    customers = [
        ("John Doe", "customer1@email.com", create_billing_statement("John Doe", [
            ("Web Hosting (1 year)", 120.00),
            ("Domain Registration", 15.00),
            ("SSL Certificate", 75.00)
        ], 210.00)),
        ("Jane Smith", "customer2@email.com", create_billing_statement("Jane Smith", [
            ("SEO Consultation (5 hours)", 500.00),
            ("Content Writing (2000 words)", 200.00),
            ("Social Media Management (1 month)", 300.00)
        ], 1000.00)),
        ("Acme Corp", "customer3@email.com", create_billing_statement("Acme Corp", [
            ("Custom Software Development (40 hours)", 4000.00),
            ("Server Upgrade", 1500.00),
            ("Employee Training Session", 800.00)
        ], 6300.00))
    ]

    for name, email, statement in customers:
        cursor.execute('''
        INSERT OR IGNORE INTO billing_customers (name, email, billing_statement)
        VALUES (?, ?, ?)
        ''', (name, email, statement))

    conn.commit()
    conn.close()

def create_billing_statement(customer_name, items, total):
    now = datetime.now()
    due_date = now + timedelta(days=30)

    statement = f"""
INVOICE

Bill To: {customer_name}
Invoice Date: {now.strftime('%Y-%m-%d')}
Due Date: {due_date.strftime('%Y-%m-%d')}

Items:
"""
    for item, price in items:
        statement += f"- {item}: ${price:.2f}\n"

    statement += f"""
Subtotal: ${total:.2f}
Tax (10%): ${total * 0.1:.2f}
Total Due: ${total * 1.1:.2f}

Please remit payment by the due date. Thank you for your business!
"""
    return statement

def view_database():
    import tkinter as tk
    from tkinter import ttk, messagebox
    conn = sqlite3.connect('billing_db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM billing_customers")
    records = cursor.fetchall()
    conn.close()
    display_records(records)

def display_records(records):
    for item in tree.get_children():
        tree.delete(item)
    
    for record in records:
        tree.insert('', 'end', values=record)

def main():
    user_input = input("Do you approve using tkinter? (yes/no): ").strip().lower()
    if user_input != "yes":
        print("tkinter won't be imported. Exiting...")
        return

    import tkinter as tk
    from tkinter import ttk, messagebox

    root = tk.Tk()
    root.title("Billing Database Manager")
    root.geometry("800x600")

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    view_btn = tk.Button(button_frame, text="Refresh Database View", command=view_database)
    view_btn.pack(side=tk.LEFT, padx=5)

    init_btn = tk.Button(button_frame, text="Initialize Database", command=initialize_database)
    init_btn.pack(side=tk.LEFT, padx=5)

    global tree
    tree = ttk.Treeview(root, columns=("ID", "Name", "Email", "Billing Statement"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Email", text="Email")
    tree.heading("Billing Statement", text="Billing Statement")

    tree.column("ID", width=50)
    tree.column("Name", width=150)
    tree.column("Email", width=200)
    tree.column("Billing Statement", width=400)
    
    tree.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)
    tree.bind("<Double-1>", on_double_click)

    scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    view_database()

    root.mainloop()

def on_double_click(event):
    item = tree.selection()[0]
    values = tree.item(item, "values")
    show_details(values)

def show_details(values):
    import tkinter as tk
    from tkinter import ttk, messagebox
    details_window = tk.Toplevel(root)
    details_window.title(f"Billing Details for {values[1]}")
    details_window.geometry("600x400")
    
    tk.Label(details_window, text=f"ID: {values[0]}").pack(anchor="w", padx=10, pady=5)
    tk.Label(details_window, text=f"Name: {values[1]}").pack(anchor="w", padx=10, pady=5)
    tk.Label(details_window, text=f"Email: {values[2]}").pack(anchor="w", padx=10, pady=5)
    
    tk.Label(details_window, text="Billing Statement:").pack(anchor="w", padx=10, pady=5)
    statement_text = tk.Text(details_window, wrap=tk.WORD, width=70, height=20)
    statement_text.insert(tk.END, values[3])
    statement_text.config(state=tk.DISABLED)
    statement_text.pack(padx=10, pady=5)

if __name__ == "__main__":
    main()
