import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import csv

# Database setup
def initialize_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="event_management"
    )
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            date DATE NOT NULL,
            location VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# CRUD Operations
def add_event(title, date, location):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="event_management"
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (title, date, location) VALUES (%s, %s, %s)", (title, date, location))
    conn.commit()
    conn.close()

def get_events(search_term=None):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="event_management"
    )
    cursor = conn.cursor()
    if search_term:
        query = "SELECT * FROM events WHERE title LIKE %s OR location LIKE %s"
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
    else:
        cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_event(event_id, title, date, location):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="event_management"
    )
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET title = %s, date = %s, location = %s WHERE id = %s", (title, date, location, event_id))
    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="event_management"
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
    conn.commit()
    conn.close()

# NEW: Export Events to CSV
def export_to_csv():
    events = get_events()
    if not events:
        messagebox.showinfo("Info", "No events available to export.")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Export Events as CSV"
    )
    if not file_path:
        return

    try:
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Title", "Date", "Location"])
            writer.writerows(events)
        messagebox.showinfo("Success", f"Events exported successfully to {file_path}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export events.\n{e}")

# NEW: Import Events from CSV
def import_from_csv():
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        title="Import Events from CSV"
    )
    if not file_path:
        return

    try:
        with open(file_path, mode="r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="event_management"
            )
            cursor = conn.cursor()
            for row in reader:
                if len(row) == 3:  # Ensure the CSV has valid format
                    cursor.execute("INSERT INTO events (title, date, location) VALUES (%s, %s, %s)", tuple(row))
            conn.commit()
            conn.close()
        messagebox.showinfo("Success", "Events imported successfully!")
        refresh_table()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import events.\n{e}")

# Tkinter UI
def main_app():
    def refresh_table(search_term=None):
        for row in tree.get_children():
            tree.delete(row)
        for event in get_events(search_term):
            tree.insert("", "end", values=event)

    def add_event_ui():
        def save():
            title = title_entry.get()
            date = date_entry.get()
            location = location_entry.get()

            if title and date and location:
                add_event(title, date, location)
                messagebox.showinfo("Success", "Event added successfully!")
                refresh_table()
                add_window.destroy()
            else:
                messagebox.showwarning("Error", "All fields are required.")

        add_window = tk.Toplevel(root)
        add_window.title("Add Event")

        tk.Label(add_window, text="Title:").grid(row=0, column=0, padx=10, pady=10)
        title_entry = tk.Entry(add_window)
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10)
        date_entry = tk.Entry(add_window)
        date_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Location:").grid(row=2, column=0, padx=10, pady=10)
        location_entry = tk.Entry(add_window)
        location_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(add_window, text="Save", command=save).grid(row=3, columnspan=2, pady=10)

    def update_event_ui():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "No event selected.")
            return

        event_id = tree.item(selected_item[0], "values")[0]
        current_title = tree.item(selected_item[0], "values")[1]
        current_date = tree.item(selected_item[0], "values")[2]
        current_location = tree.item(selected_item[0], "values")[3]

        def save():
            title = title_entry.get()
            date = date_entry.get()
            location = location_entry.get()

            if title and date and location:
                update_event(event_id, title, date, location)
                messagebox.showinfo("Success", "Event updated successfully!")
                refresh_table()
                update_window.destroy()
            else:
                messagebox.showwarning("Error", "All fields are required.")

        update_window = tk.Toplevel(root)
        update_window.title("Update Event")

        tk.Label(update_window, text="Title:").grid(row=0, column=0, padx=10, pady=10)
        title_entry = tk.Entry(update_window)
        title_entry.insert(0, current_title)
        title_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(update_window, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=10)
        date_entry = tk.Entry(update_window)
        date_entry.insert(0, current_date)
        date_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(update_window, text="Location:").grid(row=2, column=0, padx=10, pady=10)
        location_entry = tk.Entry(update_window)
        location_entry.insert(0, current_location)
        location_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(update_window, text="Save", command=save).grid(row=3, columnspan=2, pady=10)

    def delete_event_ui():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Error", "No event selected.")
            return

        event_id = tree.item(selected_item[0], "values")[0]
        delete_event(event_id)
        messagebox.showinfo("Success", "Event deleted successfully!")
        refresh_table()

    def search_events():
        search_term = search_entry.get()
        refresh_table(search_term)

    root = tk.Tk()
    root.title("Event Management System")

    # Search Bar
    search_frame = tk.Frame(root)
    search_frame.pack(fill=tk.X, padx=10, pady=5)

    tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    tk.Button(search_frame, text="Search", command=search_events).pack(side=tk.LEFT, padx=5)

    # Table
    columns = ("ID", "Title", "Date", "Location")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Buttons
    button_frame = tk.Frame(root)
    button_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Button(button_frame, text="Add Event", command=add_event_ui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Update Event", command=update_event_ui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Delete Event", command=delete_event_ui).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Export to CSV", command=export_to_csv).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Import from CSV", command=import_from_csv).pack(side=tk.LEFT, padx=5)

    refresh_table()
    root.mainloop()

if __name__ == "__main__":
    initialize_database()
    main_app()
