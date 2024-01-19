import tkinter as tk
from tkinter import ttk
from page_parser import *
from pyppeteer_check import *
import asyncio
import webbrowser
import os
import google.generativeai as genai

# Read environment variables from .env file
with open('.env', 'r') as env_file:
    for line in env_file:
        key, value = line.strip().split('=')
        os.environ[key] = value

genai.configure(api_key=os.getenv('API_KEY'))

# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config)

chat = model.start_chat(history=[])

def new_fetch_vacancy(vacancy_url):
    print(f'fetch url: {vacancy_url}')
    dynamic_webpage = ['indeed', 'careerjet', 'careerone', 'jora', 'glassdoor']
    if any(x in vacancy_url for x in dynamic_webpage):
        title, text = asyncio.run(get_details_indeed(vacancy_url))

    else:
        title, text = get_page(vacancy_url)

    print(f'Title: {title}')
    jd_textbox.delete("1.0", "end")
    jd_textbox.insert("1.0", text)

    # Checking JD contains PR or Citizenship
    keywords = ['citizen', 'citizenship' 'permanent residency', 'permanent resident']
    checkbox_var.set(any(keyword in jd_textbox.get("1.0", tk.END).lower() for keyword in keywords))

    return title, text

def select_all_text(event):
    event.widget.select_range(0, tk.END)

def open_url(event):
    webbrowser.open_new_tab(url_textbox.get())

def load_resume():
    file_path = "resume.txt"
    try:
        with open(file_path, 'r') as file:
            resume_textbox.delete("1.0", tk.END)
            resume_textbox.insert(tk.END, file.read())
    except FileNotFoundError:
        print(f"File not found: {file_path}")

def submit_form():
    jd_text = jd_textbox.get("1.0", "end-1c")
    resume_text = resume_textbox.get("1.0", "end-1c")


    if url_textbox.get() == "":
        print("Please provide URL")
        return
    if jd_text == "":
        print("Please load Job Description")
        return
    if resume_text == "":
        print("Please provide Resume")
        return

    prompt_parts = [
    "based on this resume" + resume_text + "and the following job description" + jd_text + \
        "generate cover letter for given position addressing to key points of job description"]

    generate_content(prompt_parts)

def generate_content(prompt_parts):
    # Disable the button during processing
    submit_button.config(state="disabled")
    copy_button.config(state="disabled")
    # Display processing message
    cover_letter_textbox.delete("1.0", "end")
    cover_letter_textbox.insert("1.0", "\n\nProcessing...")

    # Center the text
    cover_letter_textbox.tag_configure("center", justify="center", font=("calibri", 24))
    cover_letter_textbox.tag_add("center", "1.0", "end")

    # Update the GUI to show the processing message
    root.update_idletasks()
    # response = model.generate_content(prompt_parts)
    response = chat.send_message(prompt_parts)
    cover_letter_textbox.delete("1.0", "end")
    cover_letter_textbox.insert("1.0", response.text)

    # Enable the button after processing is complete
    submit_button.config(state="normal")
    copy_button.config(state="normal")
    # Update the GUI to ensure the message is displayed immediately
    root.update_idletasks()

def copy_to_clipboard():
    result = cover_letter_textbox.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(result)

def add_query(event):
    query = prompt_entry.get()
    generate_content(query)

root = tk.Tk()
root.title("Cover Letter Generator")
root.geometry("800x700")
root.iconbitmap("icon.ico")
root.resizable(True, True)
root.configure(padx=10, pady=10)
root.option_add("*Font", "calibri 12")
#Set the font for the Label widget
root.option_add("*Label.Font", "calibri 12 bold")

url_frame = tk.Frame(root)
url_frame.pack(fill="x", pady=(0, 5))
url_label = tk.Label(url_frame, text="Job URL:")
url_label.pack(side="left", padx=(0, 5))
open_url_icon = tk.PhotoImage(file='link.png')
open_url_button = ttk.Button(url_frame, image=open_url_icon, command=lambda: open_url(None))
open_url_button.pack(side="right")
url_textbox = tk.Entry(url_frame)
url_textbox.pack(fill="x", expand=True)
url_textbox.bind("<FocusIn>", select_all_text)
url_textbox.bind("<Return>", open_url)


jd_frame = tk.Frame(root)
jd_frame.pack(fill="x", pady=(0, 5))
jd_label = tk.Label(jd_frame, text="Job Description:")
jd_label.pack(side="left", padx=(0, 5))
load_jd_button = tk.Button(jd_frame, text="Load Job Description", command=lambda: new_fetch_vacancy(url_textbox.get()))
load_jd_button.pack(side="left", padx=(10, 0))

# Checkbox to indicate whether the JD contains specified keywords
checkbox_var = tk.BooleanVar()
citizenship_checkbox = tk.Checkbutton(jd_frame, text="Citizenship", variable=checkbox_var)
citizenship_checkbox.pack(side="left", padx=(25, 0))

jd_textbox = tk.Text(root, height=6, width=50)
jd_textbox.pack(fill="both", expand=True)

resume_frame = tk.Frame(root)
resume_frame.pack(fill="x", pady=(5, 5))
resume_label = tk.Label(resume_frame, text="Resume Text:")
resume_label.pack(side="left", padx=(0, 5))
load_resume_button = tk.Button(resume_frame, text="Load Resume", command=load_resume)
load_resume_button.pack(side="left", padx=(10, 0))

resume_textbox = tk.Text(root, height=6, width=50)
resume_textbox.pack(fill="both", expand=True)

cover_letter_label = tk.Label(root, text="Cover Letter:")
cover_letter_label.pack(anchor="w",  pady=(5, 5), padx=(0, 5))
cover_letter_textbox = tk.Text(root, height=10, width=50)
cover_letter_textbox.pack(fill="both", expand=True)

prompt_frame = tk.Frame(root)
prompt_frame.pack(fill="x", pady=(5, 5))
prompt_label = tk.Label(prompt_frame, text="Prompt:")
prompt_label.pack(side="left", padx=(0, 5))
prompt_send_icon = tk.PhotoImage(file='send.png')
prompt_send_button = ttk.Button(prompt_frame, image=prompt_send_icon, command=lambda: add_query(None))
prompt_send_button.pack(side="right")
prompt_entry = tk.Entry(prompt_frame)
prompt_entry.pack(fill="both", expand=True)
prompt_entry.bind("<FocusIn>", select_all_text)
prompt_entry.bind("<Return>", add_query)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)
submit_button = tk.Button(button_frame, text="Generate Cover Letter", command=submit_form, width=20, height=2)
submit_button.pack(side="left", padx=10)
copy_button = tk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard, width=20, height=2)
copy_button.pack(side="right", padx=10)

root.mainloop()