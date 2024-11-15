import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
from datetime import datetime, timedelta
import time
import threading
import pygame
import os
import json
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
from win10toast import ToastNotifier

# Initialize pygame mixer for playing sounds
pygame.mixer.init()

# Icon paths
ICON_PATH = 'alarm_alert_bell_internet_notice_notification_security_icon_127089.ico'

# Global vars
tasks_file = "tasks.json"
notifications_file = "notifications.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return []

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f)

# Notification functions
def log_notification(heading, message):
    with open('notification_log.txt', 'a') as log_file:
        log_file.write(f"{datetime.now()}: {heading} - {message}\n")

def snooze_notification(child, minutes=5):
    snooze_time = datetime.now() + timedelta(minutes=minutes)
    update_tree_item(child, snooze_time)

def update_tree_item(child, new_time):
    new_date = new_time.strftime("%d-%m-%Y")
    new_time_str = new_time.strftime("%I:%M %p")
    values = tree.item(child, 'values')
    tree.item(child, values=(new_date, new_time_str, *values[2:]))

def play_sound(path):
    try:
        if path and path != "None":
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
    except Exception as e:
        print(f"Error playing sound: {e}")

def notify_windows(title, message):
    try:
        toaster = ToastNotifier()
        toaster.show_toast(title, message, icon_path=ICON_PATH, duration=10)
    except Exception as e:
        print(f"Error showing notification: {e}")

def check_notifications():
    while True:
        now = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        for child in tree.get_children():
            values = tree.item(child, 'values')
            notif_time = f"{values[0]} {values[1]}"
            if now == notif_time:
                play_sound(values[5])
                notify_windows(values[3], values[4])
                log_notification(values[3], values[4])
                if messagebox.askyesno("Notification", f"Snooze for 5 minutes?"):
                    snooze_notification(child)
                else:
                    recurrence = values[6]
                    if recurrence == "None":
                        tree.delete(child)
                    else:
                        new_notif_time = update_recurrence(datetime.strptime(notif_time, "%d-%m-%Y %I:%M %p"), recurrence)
                        if new_notif_time:
                            update_tree_item(child, new_notif_time)
        time.sleep(1)

def update_recurrence(dt, recurrence):
    if recurrence == "Daily":
        return dt + timedelta(days=1)
    if recurrence == "Weekly":
        return dt + timedelta(weeks=1)
    if recurrence == "Monthly":
        return dt.replace(day=1, month=(dt.month % 12) + 1)
    return None

def save_notification():
    notification = {
        "date": f"{day_var.get()}-{month_var.get()}-{year_var.get()}",
        "time": f"{hour_var.get()}:{minute_var.get()} {am_pm_var.get()}",
        "category": category_var.get(),
        "heading": heading_var.get(),
        "message": message_entry.get("1.0", tk.END).strip(),
        "alarm": alarm_var.get() if alarm_var.get() != "Select Alarm Sound" else "None",
        "recurrence": recurrence_var.get()
    }
    if validate_notification(notification):
        tree.insert("", tk.END, values=tuple(notification.values()))
        save_data()

def validate_notification(notification):
    return all(notification.values()) and notification['recurrence'] in ["None", "Daily", "Weekly", "Monthly"]

def save_data():
    notifications = [tree.item(child, 'values') for child in tree.get_children()]
    save_json(notifications_file, notifications)

def load_data():
    for notif in load_json(notifications_file):
        tree.insert("", tk.END, values=notif)

# Stopwatch and To-Do functions
def open_stopwatch():
    def update_time():
        if is_running[0]:
            elapsed_time[0] += 1
            formatted_time = time.strftime('%H:%M:%S', time.gmtime(elapsed_time[0]))
            stopwatch_label.config(text=formatted_time)
            window.after(1000, update_time)

    def control_stopwatch(start=False, reset=False):
        if start:
            is_running[0] = True
            update_time()
        elif reset:
            is_running[0] = False
            elapsed_time[0] = 0
            stopwatch_label.config(text="00:00:00")
        else:
            is_running[0] = False

    window = Toplevel(root)
    window.title("Stopwatch")
    window.geometry("300x300")
    stopwatch_label = tk.Label(window, text="00:00:00", font=("Helvetica", 30))
    stopwatch_label.pack(pady=20)
    is_running, elapsed_time = [False], [0]

    ttk.Button(window, text="Start", command=lambda: control_stopwatch(start=True)).pack()
    ttk.Button(window, text="Stop", command=lambda: control_stopwatch()).pack()
    ttk.Button(window, text="Reset", command=lambda: control_stopwatch(reset=True)).pack()

def open_todo_list():
    window = Toplevel(root)
    window.title("To-Do List")
    window.geometry("400x400")
    
    task_listbox = tk.Listbox(window, height=15, width=50)
    task_listbox.pack(pady=10)
    
    def manage_tasks(add=False):
        task = task_entry.get() if add else None
        if add and task:
            task_listbox.insert(tk.END, task)
            task_entry.delete(0, tk.END)
        elif not add:
            task_listbox.delete(task_listbox.curselection())
        save_json(tasks_file, task_listbox.get(0, tk.END))

    task_entry = tk.Entry(window, width=30)
    task_entry.pack(pady=10)
    ttk.Button(window, text="Add Task", command=lambda: manage_tasks(add=True)).pack()
    ttk.Button(window, text="Delete Task", command=manage_tasks).pack()

    for task in load_json(tasks_file):
        task_listbox.insert(tk.END, task)

# System tray icon
def setup_system_tray():
    def create_image():
        image = Image.new('RGB', (64, 64), (0, 0, 0))
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill=(0, 0, 255))
        return image

    icon = Icon("Notifier", create_image(), "Notifier App", menu=Menu(
        MenuItem('Open', lambda: root.deiconify()),
        MenuItem('Quit', lambda: root.quit())
    ))
    icon.run()

def on_closing():
    root.withdraw()
    messagebox.showinfo("Minimized", "App minimized to tray. Right-click tray icon to restore or quit.")

# Main app UI
root = tk.Tk()
root.title("Desktop Notifier App")
root.geometry("800x600")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Setup fields
day_var, month_var, year_var = tk.StringVar(value="DD"), tk.StringVar(value="MM"), tk.StringVar(value="YYYY")
hour_var, minute_var, am_pm_var = tk.StringVar(value="HH"), tk.StringVar(value="MM"), tk.StringVar(value="AM")
category_var, heading_var, alarm_var = tk.StringVar(value="Select"), tk.StringVar(), tk.StringVar(value="Select Alarm Sound")
recurrence_var = tk.StringVar(value="None")

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.X)

# Form widgets
# Updated form fields for proper unpacking
form_fields = [
    ("Date", [(day_var, "DD", 32), (month_var, "MM", 13), (year_var, "YYYY", 2031)]),
    ("Time", [(hour_var, "HH", 13), (minute_var, "MM", 60), (am_pm_var, "AM/PM", ["AM", "PM"])]),
    ("Category", [(category_var, "Select", ["Work", "Personal", "Other"])]),
    ("Heading", [(heading_var, None, None)]),  # Added a placeholder for `opt`
    ("Message", [(None, None, None)]),  # Placeholder for Text widget (no options needed)
    ("Alarm Sound", [(alarm_var, "Select Alarm Sound", None)]),
    ("Recurrence", [(recurrence_var, "None", ["None", "Daily", "Weekly", "Monthly"])])
]

for i, (label, fields) in enumerate(form_fields):
    tk.Label(frame, text=f"{label}:", font=("Helvetica", 10)).grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
    for j, field in enumerate(fields):
        var, default, opt = field if len(field) == 3 else (field[0], field[1], None)  # Unpack with condition
        if isinstance(opt, list):
            tk.OptionMenu(frame, var, *opt).grid(row=i, column=j + 1)
        elif var:
            tk.Entry(frame, textvariable=var).grid(row=i, column=j + 1)


message_entry = tk.Text(frame, height=3)
message_entry.grid(row=5, column=1, columnspan=2)

# Treeview setup
tree = ttk.Treeview(root, columns=("Date", "Time", "Category", "Heading", "Message", "Alarm", "Recurrence"), show="headings")
for col in tree['columns']:
    tree.heading(col, text=col)
tree.pack(fill=tk.BOTH, expand=True)

# Load notifications
load_data()

# Buttons
ttk.Button(root, text="Save Notification", command=save_notification).pack(side=tk.LEFT, padx=10, pady=10)
ttk.Button(root, text="Stopwatch", command=open_stopwatch).pack(side=tk.LEFT, padx=10)
ttk.Button(root, text="To-Do List", command=open_todo_list).pack(side=tk.LEFT, padx=10)

# Start background threads
threading.Thread(target=check_notifications, daemon=True).start()
threading.Thread(target=setup_system_tray, daemon=True).start()

root.mainloop()
