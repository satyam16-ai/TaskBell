import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel, scrolledtext
import time
import threading
from datetime import datetime, timedelta
import pygame
# from win10toast import ToastNotifier
import os
import json
from PIL import Image, ImageDraw
import pystray
import requests
import platform
from plyer import notification

# Initialize pygame mixer for playing sounds
pygame.mixer.init()

# Paths to icons
window_icon = 'alarm_alert_bell_internet_notice_notification_security_icon_127089.ico'
notification_icon = 'alarm_alert_bell_internet_notice_notification_security_icon_127089.ico'
def open_stopwatch():
    stopwatch_window = Toplevel(root)
    stopwatch_window.title("Stopwatch")
    stopwatch_window.geometry("300x300")

    # Keep the stopwatch window on top
    stopwatch_window.wm_attributes("-topmost", 1)

    stopwatch_label = tk.Label(stopwatch_window, text="00:00:00", font=("Helvetica", 30))
    stopwatch_label.pack(pady=20)

    is_running = [False]  # To track whether the stopwatch is running
    is_timer_running = [False]  # To track whether the timer is running
    elapsed_time = [0]  # Elapsed time in seconds for stopwatch
    timer_seconds = [0]  # Store timer duration in seconds

    def update_time():
        """Update the stopwatch display every second."""
        if is_running[0]:
            elapsed_time[0] += 1
            formatted_time = time.strftime('%H:%M:%S', time.gmtime(elapsed_time[0]))
            stopwatch_label.config(text=formatted_time)
            stopwatch_window.after(1000, update_time)

    def start_stopwatch():
        """Start the stopwatch."""
        if not is_running[0] and not is_timer_running[0]:  # Prevent starting if timer is running
            is_running[0] = True
            update_time()

    def stop():
        """Stop both the stopwatch and the timer."""
        is_running[0] = False
        is_timer_running[0] = False

    def reset():
        """Reset both the stopwatch and the timer."""
        is_running[0] = False
        is_timer_running[0] = False
        elapsed_time[0] = 0
        timer_seconds[0] = 0
        stopwatch_label.config(text="00:00:00")

    def set_timer():
        """Set a timer and count down."""
        try:
            timer_minutes = int(timer_entry.get())
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid number.")
            return

        if not is_timer_running[0] and not is_running[0]:  # Prevent starting if stopwatch is running
            timer_seconds[0] = timer_minutes * 60
            is_timer_running[0] = True
            countdown()

    def countdown():
        """Handle the countdown for the timer."""
        if timer_seconds[0] > 0 and is_timer_running[0]:
            mins, secs = divmod(timer_seconds[0], 60)
            formatted_time = '{:02d}:{:02d}'.format(mins, secs)
            stopwatch_label.config(text=formatted_time)
            timer_seconds[0] -= 1
            stopwatch_window.after(1000, countdown)
        else:
            if is_timer_running[0]:  # Play sound only if timer was running
                play_stopwatch_end_sound()
                messagebox.showinfo("Timer Done", "Time's up!")
            is_timer_running[0] = False  # Stop the timer

    def play_stopwatch_end_sound():
        """Play a sound when the timer ends."""
        pygame.mixer.music.load("stopwatch_end_sound.mp3")  # Ensure you have this sound file
        pygame.mixer.music.play()

    # Timer Entry
    timer_frame = tk.Frame(stopwatch_window)
    timer_frame.pack(pady=10)

    tk.Label(timer_frame, text="Set Timer (Minutes):").pack(side=tk.LEFT, padx=5)
    timer_entry = tk.Entry(timer_frame, width=5)
    timer_entry.pack(side=tk.LEFT)

    tk.Button(stopwatch_window, text="Start Timer", command=set_timer).pack(pady=10)

    # Control Buttons for Stopwatch and Timer
    control_frame = tk.Frame(stopwatch_window)
    control_frame.pack(pady=10)

    tk.Button(control_frame, text="Start Stopwatch", command=start_stopwatch).pack(side=tk.LEFT, padx=5)
    tk.Button(control_frame, text="Stop", command=stop).pack(side=tk.LEFT, padx=5)
    tk.Button(control_frame, text="Reset", command=reset).pack(side=tk.LEFT, padx=5)

def open_todo_list():
    todo_window = Toplevel(root)
    todo_window.title("To-Do List")
    todo_window.geometry("400x400")

    task_listbox = tk.Listbox(todo_window, height=15, width=50)
    task_listbox.pack(pady=10)

    task_entry = tk.Entry(todo_window, width=30)
    task_entry.pack(pady=10)

    add_task_button = tk.Button(todo_window, text="Add Task", command=lambda: add_task(task_entry, task_listbox))
    add_task_button.pack(pady=10)

    delete_task_button = tk.Button(todo_window, text="Delete Task", command=lambda: delete_task(task_listbox))
    delete_task_button.pack(pady=5)

    # Load saved tasks
    load_tasks(task_listbox)
def add_task(task_entry, task_listbox):
    task = task_entry.get()
    if task:
        task_listbox.insert(tk.END, task)
        task_entry.delete(0, tk.END)
        save_tasks(task_listbox)

def delete_task(task_listbox):
    try:
        selected_task_index = task_listbox.curselection()[0]
        task_listbox.delete(selected_task_index)
        save_tasks(task_listbox)
    except IndexError:
        messagebox.showwarning("Select Task", "Please select a task to delete.")

def save_tasks(task_listbox):
    tasks = task_listbox.get(0, tk.END)
    with open("tasks.json", "w") as file:
        json.dump(tasks, file)

def load_tasks(task_listbox):
    if os.path.exists("tasks.json"):
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
            for task in tasks:
                task_listbox.insert(tk.END, task)    

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
                if (alarm_sound_path and alarm_sound_path != "None"):
                    try:
                        pygame.mixer.music.load(alarm_sound_path)
                        pygame.mixer.music.play()
                    except Exception as e:
                        print(f"Error playing sound: {e}")

                # Show notification
                notify(values[3], values[4])

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

# def notify_windows(title, message):
#     try:
#         toaster = ToastNotifier()
#         toaster.show_toast(
#             title,
#             message,
#             icon_path=notification_icon,
#             duration=10
#         )
#     except Exception as e:
#         print(f"Error showing notification: {e}")

def notify(title, message):
    notification.notify(
        title=title,
        message=message,
        app_icon=notification_icon,
        timeout=10
    )

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
def fetch_weather(city):
    api_key = 'aec27642d2d44100a25113139241209'  # Replace with your WeatherAPI key
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&aqi=no"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'current' in data:
            weather_info = {
                'city': city,
                'temperature': data['current']['temp_c'],
                'condition': data['current']['condition']['text'],
                'humidity': data['current']['humidity'],
                'wind': data['current']['wind_kph']
            }
            return weather_info
        else:
            return {'error': 'City not found or API error'}
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

def display_weather():
    city = city_entry.get()
    weather_info = fetch_weather(city)
    
    if 'error' in weather_info:
        weather_label.config(text=weather_info['error'])
    else:
        weather_label.config(
            text=f"City: {weather_info['city']}\n"
                 f"Temperature: {weather_info['temperature']}°C\n"
                 f"Condition: {weather_info['condition']}\n"
                 f"Humidity: {weather_info['humidity']}%\n"
                 f"Wind: {weather_info['wind']} kph"
        )

# Main Application Window
root = tk.Tk()
root.title("Desktop Notifier App with AI Assistant")
root.geometry("800x800")  # Increased height to accommodate the new section

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

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

# Existing UI elements...

# AI Assistant Frame
ai_frame = ttk.Frame(root)
ai_frame.place(relx=0.75, rely=0.05, anchor="n")  # Positioning at the top right

tk.Label(ai_frame, text="AI Personal Assistant", font=("Helvetica", 14)).pack(pady=10)

ai_input_frame = ttk.Frame(ai_frame)
ai_input_frame.pack(pady=10, fill=tk.X)

tk.Label(ai_input_frame, text="Ask me anything:", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=5)
ai_query_entry = tk.Entry(ai_input_frame, width=50)
ai_query_entry.pack(side=tk.LEFT, padx=5)

def get_ai_response():
    query = ai_query_entry.get()
    if query:
        # Your Cohere API key
        api_key = "d0nqMxyPxnvXaja5bisTk6cKLZwQfmXMgO4lejhb"
        url = "https://api.cohere.ai/generate"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "command-xlarge-nightly",  # Ensure the model name is correct
            "prompt": query,
            "max_tokens": 50,
            "temperature": 0.7
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            print("API Response:", response.json())  # Debugging: Print full API response

            if response.status_code == 200:
                # Extract the response text directly from 'text' key
                response_json = response.json()
                ai_response = response_json.get("text", "No response from AI")
            else:
                ai_response = f"Error: {response.status_code} - {response.json().get('message', 'Unknown error')}"

            # Display the response
            ai_response_text.config(state=tk.NORMAL)
            ai_response_text.insert(tk.END, f"User: {query}\nAI: {ai_response}\n\n")
            ai_response_text.config(state=tk.DISABLED)
            ai_query_entry.delete(0, tk.END)

        except Exception as e:
            ai_response_text.config(state=tk.NORMAL)
            ai_response_text.insert(tk.END, f"Error: {str(e)}\n")
            ai_response_text.config(state=tk.DISABLED)

tk.Button(ai_input_frame, text="Submit", command=get_ai_response).pack(side=tk.LEFT, padx=5)

ai_response_text = scrolledtext.ScrolledText(ai_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
ai_response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Existing UI elements...

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

weather_frame = ttk.Frame(root)
weather_frame.pack(pady=10)

tk.Label(weather_frame, text="Enter City:", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=5)
city_entry = tk.Entry(weather_frame, width=20)
city_entry.pack(side=tk.LEFT, padx=5)

tk.Button(weather_frame, text="Get Weather", command=display_weather).pack(side=tk.LEFT, padx=5)

weather_label = tk.Label(weather_frame, text="", font=("Helvetica", 10))
weather_label.pack(pady=10)

# Start system tray icon
threading.Thread(target=setup_system_tray, daemon=True).start()
todo_menu = tk.Menu(menu_bar, tearoff=0)
stopwatch_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Stopwatch", menu=stopwatch_menu)
stopwatch_menu.add_command(label="Open Stopwatch", command=open_stopwatch)
menu_bar.add_cascade(label="To-Do List", menu=todo_menu)
todo_menu.add_command(label="Open To-Do List", command=open_todo_list)

# Set up the close event handler
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()