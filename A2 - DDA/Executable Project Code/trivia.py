import tkinter as tk
from tkinter import ttk
import requests
import random
import time
import threading
import pygame  # pygame is used for the sound of the correct and wrong answer
import re
import unicodedata


pygame.mixer.init()

# --- sound files for the right and wrong sound ---
correct_sound = pygame.mixer.Sound("C:\\Users\\ASUS\\Downloads\\assessment 2 advanced programming\\correct sound.wav.mp3")
wrong_sound = pygame.mixer.Sound("C:\\Users\\ASUS\\Downloads\\assessment 2 advanced programming\\wrong sound.wav.mp3")



# this shows the error of the coode
is_fetching_error = False

# trivia questions and answers from the  trivia api below
def fetch_questions():
    global timer_running, is_fetching_error
    timer_running = True
    category = category_var.get()
    difficulty = difficulty_var.get()

    # API link
    url = f"https://opentdb.com/api.php?amount=1&category={category_map[category]}&difficulty={difficulty}&type=multiple"

    try:
        response = requests.get(url)
        data = response.json()
        if data["response_code"] == 0:
            display_question(data["results"][0])
            is_fetching_error = False 
        else:
          
            if not is_fetching_error:
                show_popup("Error", "Failed to fetch question!")
                is_fetching_error = True 
    except Exception as e:
       
        if not is_fetching_error:
            show_popup("Error", f"Something went wrong: {e}")
            is_fetching_error = True 

# this cleans the typhographical errors and remove any unwanted letters and symbols
def clean_text(text):
   
    text = re.sub(r'[^A-Za-z0-9\s,.:;!?(){}\'"-]', '', text)
    
 
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    
   
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def display_question(question_data):
    global correct_answer, time_left

    question = clean_text(question_data["question"])

    time_left = 10
    time_label.config(text=f"Time Left: {time_left}s")

    question_label.config(text=question)
    correct_answer = question_data["correct_answer"]
    options = question_data["incorrect_answers"] + [correct_answer]
    random.shuffle(options)

    for i, option in enumerate(options):
        option_buttons[i].config(
            text=clean_text(option),  
            bg="#FAEBD7",
            fg="#2F4F4F",
            command=lambda opt=option, idx=i: check_answer(opt, idx),
            relief="solid",
            bd=1,
        )
        # hover effect for the buttons
        option_buttons[i].bind("<Enter>", lambda event, btn=option_buttons[i]: on_hover_enter(btn))
        option_buttons[i].bind("<Leave>", lambda event, btn=option_buttons[i]: on_hover_leave(btn))

    # countdown of the timer
    countdown_timer()


def countdown_timer():
    global time_left
    if time_left > 0:
        time_left -= 1
        time_label.config(text=f"Time Left: {time_left}s")
        root.after(1000, countdown_timer)
    else:
        show_time_up()


def show_time_up():
    show_popup("Oops! Time's Up!", "Next Question", 2)  # removes aftter 2 seconds
    fetch_questions()

def show_popup(title, message, auto_close_time=None):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.configure(bg="white") 

    
    popup_width = 300
    popup_height = 150
    screen_width = root.winfo_width()
    screen_height = root.winfo_height()
    position_top = int((screen_height - popup_height) / 2)
    position_left = int((screen_width - popup_width) / 2)
    
    popup.geometry(f"{popup_width}x{popup_height}+{position_left}+{position_top}")
    
    label = tk.Label(popup, text=message, bg="white", fg="#2F4F4F", font=("Arial", 12), wraplength=280, justify="center")
    label.pack(pady=20)

    button = ttk.Button(popup, text="Next Question", command=popup.destroy, style="Custom.TButton")
    button.pack(pady=10)

    if auto_close_time:
        root.after(auto_close_time * 1000, popup.destroy) 

    popup.transient(root) 
    popup.grab_set()       
    root.wait_window(popup)


def on_hover_enter(button):
    button.config(bg="#F5F5F5", fg="#2F4F4F")


def on_hover_leave(button):
    button.config(bg="#FAEBD7", fg="#2F4F4F")

# Check if the answer is correct
def check_answer(selected_option, button_index):
    global timer_running
    if timer_running:
        timer_running = False
        if selected_option == correct_answer:
            pygame.mixer.Sound.play(correct_sound)  # Play the correct sound
            option_buttons[button_index].config(bg="green") 
            show_popup("Correct Answer!", "Good job! Let's move to the next question.", 2)  
        else:
            pygame.mixer.Sound.play(wrong_sound)  # Play the wrong answer sound
            option_buttons[button_index].config(bg="red")  
            show_popup("Wrong Answer!", f"The correct answer was: {correct_answer}", 2)  

        fetch_questions()

# --- animation---

def animate_startup():
    for alpha in range(0, 11):  
        root.attributes('-alpha', alpha / 10.0)
        time.sleep(0.05)  # start up transition 

   
    for offset in range(-100, 1, 5):  
        frame.place_configure(rely=(offset / 100.0))
        time.sleep(0.01)



# Main window
root = tk.Tk()
root.title("Trivia Quiz")
root.geometry("600x700")
root.configure(bg="white")
root.attributes('-alpha', 0.0)  


category_var = tk.StringVar(value="General Knowledge")
difficulty_var = tk.StringVar(value="easy")
correct_answer = ""
time_left = 10
timer_running = False

category_map = {
    "General Knowledge": 9,
    "Books": 10,
    "Film": 11,
    "Music": 12,
    "Science & Nature": 17,
    "Computers": 18,
    "Mathematics": 19,
}

# --- canvas to appear the notebook background style and lines---
def draw_notebook_lines():
    width = root.winfo_width()
    height = root.winfo_height()
    canvas.delete("all")
    for i in range(0, height, 20):
        canvas.create_line(0, i, width, i, fill="#D3D3D3", width=1)

canvas = tk.Canvas(root, bg="white")
canvas.pack(fill="both", expand=True)
root.bind("<Configure>", lambda event: draw_notebook_lines())

# main frame with background
frame = tk.Frame(root, bg="#FAEBD7", bd=10, relief="solid", padx=20, pady=20)
frame.place(relwidth=0.9, relheight=0.9, relx=0.05, rely=-1.0)  # Start off-screen

# title of the quiz
title_label = tk.Label(frame, text="📒 Trivia Quiz 📒", font=("Arial", 28, "bold"), bg="#FAEBD7", fg="#2F4F4F")
title_label.pack(pady=15)

# the cattegory and difficulty of the app
selection_frame = tk.Frame(frame, bg="#FAEBD7")
selection_frame.pack(pady=10)

ttk.Label(selection_frame, text="Select Category:", background="#FAEBD7", foreground="#2F4F4F").grid(row=0, column=0, padx=5, pady=5, sticky="w")
category_menu = ttk.Combobox(selection_frame, textvariable=category_var, values=list(category_map.keys()), state="readonly", width=25)
category_menu.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(selection_frame, text="Select Difficulty:", background="#FAEBD7", foreground="#2F4F4F").grid(row=1, column=0, padx=5, pady=5, sticky="w")
difficulty_menu = ttk.Combobox(selection_frame, textvariable=difficulty_var, values=["easy", "medium", "hard"], state="readonly", width=25)
difficulty_menu.grid(row=1, column=1, padx=5, pady=5)

fetch_button = ttk.Button(frame, text="Fetch Question", command=fetch_questions)
fetch_button.pack(pady=15)

# Timer
time_label = tk.Label(frame, text=f"Time Left: {time_left}s", font=("Arial", 16), bg="#FAEBD7", fg="#2F4F4F")
time_label.pack(pady=15)

# questions and its multiple choice 
question_label = tk.Label(frame, text="", font=("Arial", 14, "italic"), wraplength=500, bg="#FAEBD7", fg="#2F4F4F", justify="center")
question_label.pack(pady=25)

option_frame = tk.Frame(frame, bg="#FAEBD7")
option_frame.pack(pady=20)

option_buttons = []
for i in range(4):
    btn = tk.Button(option_frame, text="", width=35, height=2, bg="#FAEBD7", fg="#2F4F4F", font=("Arial", 12), relief="solid", bd=1, padx=10)
    btn.pack(pady=8)
    option_buttons.append(btn)

# foote of the app
footer = tk.Label(frame, text="✨ Ready to test your knowledge? Let’s go! ✨", font=("Helvetica", 10, "italic"), bg="#FAEBD7", fg="#2F4F4F")
footer.pack(side="bottom", pady=10)

# Start to run the app
threading.Thread(target=animate_startup).start()
root.mainloop()
