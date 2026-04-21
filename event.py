import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3

# ---------------- DATABASE ----------------
conn = sqlite3.connect("event_system.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    date TEXT,
    time TEXT,
    location TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    attendee_name TEXT,
    event_name TEXT
)
""")

# Default users
cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin','1234','admin')")
cursor.execute("INSERT OR IGNORE INTO users VALUES ('user','1234','user')")
conn.commit()

# ---------------- APP ----------------
root = tk.Tk()
root.title("Event Management System")
root.geometry("900x520")
root.config(bg="#f4f6f9")

# ---------------- PLACEHOLDER ----------------
def add_placeholder(entry, text, is_password=False):
    entry.insert(0, text)
    entry.config(fg="grey")

    def on_focus_in(e):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg="black")
            if is_password:
                entry.config(show="*")

    def on_focus_out(e):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg="grey")
            if is_password:
                entry.config(show="")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# ---------------- UTIL ----------------
def clear_screen():
    for w in root.winfo_children():
        w.destroy()

# ---------------- LOGIN ----------------
def login_screen():
    clear_screen()

    frame = tk.Frame(root, bg="white", padx=30, pady=30)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="Login", font=("Arial", 18, "bold"), bg="white").pack(pady=10)

    global user_entry, pass_entry
    user_entry = tk.Entry(frame, width=25)
    user_entry.pack(pady=5)
    add_placeholder(user_entry, "Username")

    pass_entry = tk.Entry(frame, width=25)
    pass_entry.pack(pady=5)
    add_placeholder(pass_entry, "Password", True)

    tk.Button(frame, text="Login", bg="#007bff", fg="white",
              width=20, command=login).pack(pady=10)

def login():
    username = user_entry.get().strip()
    password = pass_entry.get().strip()

    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        dashboard(result[0], username)
    else:
        messagebox.showerror("Error", "Invalid Login")

# ---------------- DASHBOARD ----------------
def dashboard(role, username):
    clear_screen()

    sidebar = tk.Frame(root, bg="#2c3e50", width=200)
    sidebar.pack(side="left", fill="y")

    content = tk.Frame(root, bg="#ecf0f1")
    content.pack(side="right", expand=True, fill="both")

    tk.Label(sidebar, text=f"{role.upper()} PANEL", fg="white",
             bg="#2c3e50", font=("Arial", 14, "bold")).pack(pady=20)

    # -------- VIEW EVENTS --------
    def show_events():
        for w in content.winfo_children():
            w.destroy()

        tk.Label(content, text="Events", font=("Arial", 16, "bold"),
                 bg="#ecf0f1").pack(pady=10)

        cols = ("Name", "Date", "Time", "Location")
        tree = ttk.Treeview(content, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)

        cursor.execute("SELECT name,date,time,location FROM events")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

        tree.pack(expand=True, fill="both", padx=20, pady=10)

        # USER REGISTER
        if role == "user":
            def register_event():
                selected = tree.selection()
                if not selected:
                    messagebox.showwarning("Select", "Select an event")
                    return

                event = tree.item(selected[0])["values"][0]

                # Ask name
                attendee = simpledialog.askstring("Register", "Enter your name:")
                if not attendee:
                    return

                cursor.execute("""
                INSERT INTO registrations (username, attendee_name, event_name)
                VALUES (?, ?, ?)
                """, (username, attendee, event))
                conn.commit()

                messagebox.showinfo("Success", f"{attendee} registered!")

            tk.Button(content, text="Register Event", bg="#2980b9", fg="white",
                      command=register_event).pack(pady=10)

    # -------- ADD EVENT (ADMIN) --------
    def add_event_page():
        for w in content.winfo_children():
            w.destroy()

        tk.Label(content, text="Add Event", font=("Arial", 16, "bold"),
                 bg="#ecf0f1").pack(pady=10)

        name = tk.Entry(content, width=30)
        name.pack(pady=5)
        add_placeholder(name, "Event Name")

        date = tk.Entry(content, width=30)
        date.pack(pady=5)
        add_placeholder(date, "Date")

        time = tk.Entry(content, width=30)
        time.pack(pady=5)
        add_placeholder(time, "Time")

        location = tk.Entry(content, width=30)
        location.pack(pady=5)
        add_placeholder(location, "Location")

        def save():
            cursor.execute("INSERT INTO events (name,date,time,location) VALUES (?,?,?,?)",
                           (name.get(), date.get(), time.get(), location.get()))
            conn.commit()
            messagebox.showinfo("Success", "Event Added")
            show_events()

        tk.Button(content, text="Save Event", bg="#27ae60", fg="white",
                  command=save).pack(pady=10)

    # -------- VIEW REGISTRATIONS (ADMIN) --------
    def view_registrations():
        for w in content.winfo_children():
            w.destroy()

        tk.Label(content, text="Registered Users", font=("Arial", 16, "bold"),
                 bg="#ecf0f1").pack(pady=10)

        cols = ("Username", "Attendee Name", "Event")
        tree = ttk.Treeview(content, columns=cols, show="headings")

        for c in cols:
            tree.heading(c, text=c)

        cursor.execute("SELECT username, attendee_name, event_name FROM registrations")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

        tree.pack(expand=True, fill="both", padx=20, pady=10)

    # -------- LOGOUT --------
    def logout():
        login_screen()

    # Sidebar buttons
    tk.Button(sidebar, text="View Events", width=20,
              command=show_events).pack(pady=5)

    if role == "admin":
        tk.Button(sidebar, text="Add Event", width=20,
                  command=add_event_page).pack(pady=5)

        tk.Button(sidebar, text="View Registrations", width=20,
                  command=view_registrations).pack(pady=5)

    tk.Button(sidebar, text="Logout", width=20, bg="red", fg="white",
              command=logout).pack(side="bottom", pady=20)

    show_events()

# ---------------- START ----------------
login_screen()
root.mainloop()
conn.close()
