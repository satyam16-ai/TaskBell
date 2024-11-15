import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import time
import threading
from datetime import datetime, timedelta
import pygame
from win10toast import ToastNotifier
import os
import json
from PIL import Image, ImageDraw
import pystray

# Initialize pygame mixer for playing sounds
pygame.mixer.init()

# Paths to icons
window_icon = 'alarm_alert_bell_internet_notice_notification_security_icon_127089.ico'
notification_icon = 'alarm_alert_bell_internet_notice_notification_security_icon_127089.ico'

def log_notification(heading, message):
    with open('notification_log.txt', 'a') as log_file:
        log_file.write(f"{datetime.now()}: {heading} - {message}\n")

def snooze_notification(minutes, child):
    snooze_time = datetime.now() + timedelta(minutes=minutes)
    new_date = snooze_time.strftime("%d-%m-%Y")
    new_time = snooze_time.strftime("%I:%M %p")
    values = tree.item(child, 'values')
    tree.item(child, values=(new_date, new_time, values[2], values[3], values[4], values[5], values[6]))

def update_recurrence(date_time, recurrence):
    if recurrence == "Daily":
        return date_time + timedelta(days=1)
    elif recurrence == "Weekly":
        return date_time + timedelta(weeks=1)
    elif recurrence == "Monthly":
        return date_time.replace(day=1, month=(date_time.month % 12) + 1)
    return None

def check_notification_time():
    while True:
        now = datetime.now().strftime("%d-%m-%Y %I:%M %p")
        for child in tree.get_children():
            values = tree.item(child, 'values')
            notif_date_time = f"{values[0]} {values[1]}"
            if now == notif_date_time:
                # Play alarm sound if set
                alarm_sound_path = values[5]
                if alarm_sound_path and alarm_sound_path != "None":
                    try:
                        pygame.mixer.music.load(alarm_sound_path)
                        pygame.mixer.music.play()
                    except Exception as e:
                        print(f"Error playing sound: {e}")

                # Show notification
                notify_windows(values[3], values[4])

                # Log notification
                log_notification(values[3], values[4])

                # Ask user to snooze or dismiss
                snooze_or_dismiss = messagebox.askyesno("Notification", f"{values[3]}\n\n{values[4]}\n\nSnooze for 5 minutes?")
                
                if snooze_or_dismiss:
                    snooze_notification(5, child)
                else:
                    # Only delete notification if recurrence is 'None'
                    recurrence = values[6]
                    if recurrence == "None":
                        tree.delete(child)
                    else:
                        notif_date_time_obj = datetime.strptime(f"{values[0]} {values[1]}", "%d-%m-%Y %I:%M %p")
                        new_notif_date_time = update_recurrence(notif_date_time_obj, recurrence)
                        if new_notif_date_time:
                            new_date = new_notif_date_time.strftime("%d-%m-%Y")
                            new_time = new_notif_date_time.strftime("%I:%M %p")
                            tree.item(child, values=(new_date, new_time, values[2], values[3], values[4], values[5], values[6]))
        time.sleep(1)  # Check every second for more responsive notifications

def notify_windows(title, message):
    try:
        toaster = ToastNotifier()
        toaster.show_toast(
            title,
            message,
            icon_path=notification_icon,
            duration=10
        )
    except Exception as e:
        print(f"Error showing notification: {e}")

def save_notification():
    date = f"{day_var.get()}-{month_var.get()}-{year_var.get()}"
    time_str = f"{hour_var.get()}:{minute_var.get()} {am_pm_var.get()}"
    category = category_var.get()
    heading = heading_entry.get()
    message = message_entry.get("1.0", tk.END).strip()
    alarm_sound = alarm_var.get()
    recurrence = recurrence_var.get()

    if (day_var.get() == "DD" or month_var.get() == "MM" or year_var.get() == "YYYY" or
        hour_var.get() == "HH" or minute_var.get() == "MM" or 
        am_pm_var.get() not in ["AM", "PM"] or category == "Select" or not heading or not message):
        messagebox.showwarning("Missing Data", "All fields are required.")
        return

    if alarm_sound == "Select Alarm Sound":
        alarm_sound = "None"

    tree.insert("", tk.END, values=(date, time_str, category, heading, message, alarm_sound, recurrence))
    save_data()

def clear_fields():
    day_var.set("DD")
    month_var.set("MM")
    year_var.set("YYYY")
    hour_var.set("HH")
    minute_var.set("MM")
    am_pm_var.set("AM")
    category_var.set("Select")
    heading_entry.delete(0, tk.END)
    message_entry.delete("1.0", tk.END)
    alarm_var.set("Select Alarm Sound")
    recurrence_var.set("None")

def delete_notification():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Select Item", "Please select a notification to delete.")
        return
    tree.delete(selected_item)
    save_data()
    messagebox.showinfo("Success", "Notification deleted successfully.")

def select_alarm_sound():
    file_path = filedialog.askopenfilename(title="Select Alarm Sound", filetypes=[("Audio Files", "*.wav;*.mp3")])
    if file_path:
        alarm_var.set(file_path)

def toggle_theme():
    current_bg = root.cget("bg")
    
    if current_bg == "#F0F0F0":
        # Switch to dark theme
        root.configure(bg="#2E2E2E")
        style.configure('TLabel', background="#2E2E2E", foreground="white")
        style.configure('TButton', background="#2E2E2E", foreground="white")
        style.configure('Treeview', background="#3C3C3C", foreground="white", fieldbackground="#3C3C3C")
        tree.configure(
            background=style.lookup('Treeview', 'background'),
            foreground=style.lookup('Treeview', 'foreground'),
            fieldbackground=style.lookup('Treeview', 'fieldbackground')
        )
    else:
        # Switch to light theme
        root.configure(bg="#F0F0F0")
        style.configure('TLabel', background="#F0F0F0", foreground="black")
        style.configure('TButton', background="#F0F0F0", foreground="black")
        style.configure('Treeview', background="white", foreground="black", fieldbackground="white")
        tree.configure(
            background=style.lookup('Treeview', 'background'),
            foreground=style.lookup('Treeview', 'foreground'),
            fieldbackground=style.lookup('Treeview', 'fieldbackground')
        )

def save_data():
    notifications = []
    for child in tree.get_children():
        values = tree.item(child, 'values')
        notifications.append({
            "date": values[0],
            "time": values[1],
            "category": values[2],
            "heading": values[3],
            "message": values[4],
            "alarm": values[5],
            "recurrence": values[6]
        })
    with open('notifications.json', 'w') as f:
        json.dump(notifications, f)

def load_data():
    if os.path.exists('notifications.json'):
        with open('notifications.json', 'r') as f:
            notifications = json.load(f)
            for notif in notifications:
                tree.insert("", tk.END, values=(
                    notif["date"], notif["time"], notif["category"], notif["heading"], notif["message"], notif["alarm"], notif["recurrence"]
                ))

def on_closing():
    root.withdraw()  # Hide the window
    show_message("The application is now running in the background. Right-click the system tray icon to quit or restore the application.")

def quit_app(icon, item):
    icon.stop()
    root.destroy()

def show_message(message):
    messagebox.showinfo("Application", message)

def create_image():
    # Create an image for the system tray icon
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width//4, height//4, width//4*3, height//4*3),
        fill=(0, 0, 255))
    return image

def setup_system_tray():
    icon = pystray.Icon("test", create_image(), "Notifier App")
    icon.menu = pystray.Menu(
        pystray.MenuItem('Open', open_app),
        pystray.MenuItem('Quit', quit_app)
    )
    icon.run()

def open_app(icon, item):
    root.deiconify()  # Show the window

# Main Application Window
root = tk.Tk()
root.title("Desktop Notifier App")
root.geometry("800x600")

style = ttk.Style()
style.configure('TLabel', background="#F0F0F0", foreground="black")
style.configure('TButton', background="#F0F0F0", foreground="black")
style.configure('Treeview', background="white", foreground="black", fieldbackground="white")

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.X)

day_var = tk.StringVar(value="DD")
month_var = tk.StringVar(value="MM")
year_var = tk.StringVar(value="YYYY")
hour_var = tk.StringVar(value="HH")
minute_var = tk.StringVar(value="MM")
am_pm_var = tk.StringVar(value="AM")
category_var = tk.StringVar(value="Select")
heading_var = tk.StringVar()
message_var = tk.StringVar()
alarm_var = tk.StringVar(value="Select Alarm Sound")
recurrence_var = tk.StringVar(value="None")

tk.Label(frame, text="Date:", font=("Helvetica", 10)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
tk.OptionMenu(frame, day_var, *[f"{i:02d}" for i in range(1, 32)]).grid(row=0, column=1, padx=5, pady=5)
tk.OptionMenu(frame, month_var, *[f"{i:02d}" for i in range(1, 13)]).grid(row=0, column=2, padx=5, pady=5)
tk.OptionMenu(frame, year_var, *[str(year) for year in range(2023, 2031)]).grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame, text="Time:", font=("Helvetica", 10)).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
tk.OptionMenu(frame, hour_var, *[f"{i:02d}" for i in range(1, 13)]).grid(row=1, column=1, padx=5, pady=5)
tk.OptionMenu(frame, minute_var, *[f"{i:02d}" for i in range(0, 60, 1)]).grid(row=1, column=2, padx=5, pady=5)
tk.OptionMenu(frame, am_pm_var, "AM", "PM").grid(row=1, column=3, padx=5, pady=5)

tk.Label(frame, text="Category:", font=("Helvetica", 10)).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
tk.OptionMenu(frame, category_var, "Work", "Personal", "Other").grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame, text="Heading:", font=("Helvetica", 10)).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
heading_entry = tk.Entry(frame, textvariable=heading_var)
heading_entry.grid(row=3, column=1, padx=5, pady=5, columnspan=3)

tk.Label(frame, text="Message:", font=("Helvetica", 10)).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
message_entry = tk.Text(frame, height=4, width=50)
message_entry.grid(row=4, column=1, padx=5, pady=5, columnspan=3)

tk.Label(frame, text="Alarm Sound:", font=("Helvetica", 10)).grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
tk.Button(frame, text="Select Sound", command=select_alarm_sound).grid(row=5, column=1, padx=5, pady=5)
tk.Label(frame, textvariable=alarm_var, font=("Helvetica", 10)).grid(row=5, column=2, padx=5, pady=5)

tk.Label(frame, text="Recurrence:", font=("Helvetica", 10)).grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
tk.OptionMenu(frame, recurrence_var, "None", "Daily", "Weekly", "Monthly").grid(row=6, column=1, padx=5, pady=5)

tk.Button(frame, text="Save Notification", command=save_notification).grid(row=7, column=0, padx=5, pady=5)
tk.Button(frame, text="Clear Fields", command=clear_fields).grid(row=7, column=1, padx=5, pady=5)
tk.Button(frame, text="Delete Notification", command=delete_notification).grid(row=7, column=2, padx=5, pady=5)

# Create Treeview
tree = ttk.Treeview(root, columns=("Date", "Time", "Category", "Heading", "Message", "Sound", "Recurrence"), show="headings")
tree.heading("Date", text="Date")
tree.heading("Time", text="Time")
tree.heading("Category", text="Category")
tree.heading("Heading", text="Heading")
tree.heading("Message", text="Message")
tree.heading("Sound", text="Sound")
tree.heading("Recurrence", text="Recurrence")

tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Load saved data
load_data()

# Start checking notifications in a separate thread
def start_checking():
    check_notification_time()

threading.Thread(target=start_checking, daemon=True).start()

# Theme Toggle Button
theme_toggle_button = tk.Button(root, text="Toggle Theme", command=toggle_theme)
theme_toggle_button.pack(pady=10)

# Start system tray icon
threading.Thread(target=setup_system_tray, daemon=True).start()

# Set up the close event handler
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
