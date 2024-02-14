import tkinter as tk
from tkinter import ttk
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

def select_all_text(event):
    event.widget.select_range(0, tk.END)

def generate_content(prompt_parts):
    # Disable the button during processing
    submit_button.config(state="disabled")
    copy_button.config(state="disabled")
    # Display processing message
    response_textbox.delete("1.0", "end")
    response_textbox.insert("1.0", "\n\nProcessing...")

    # Center the text
    response_textbox.tag_configure("center", justify="center", font=("calibri", 24))
    response_textbox.tag_add("center", "1.0", "end")

    # Update the GUI to show the processing message
    root.update_idletasks()
    # response = model.generate_content(prompt_parts)
    response = chat.send_message(prompt_parts)
    response_textbox.delete("1.0", "end")
    response_textbox.insert("1.0", response.text)

    # Enable the button after processing is complete
    submit_button.config(state="normal")
    copy_button.config(state="normal")
    # Update the GUI to ensure the message is displayed immediately
    root.update_idletasks()

def copy_to_clipboard():
    result = response_textbox.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(result)

def add_query(event):
    query = prompt_entry.get()
    generate_content(query)

root = tk.Tk()
root.title("Gemini Chat")
root.geometry("600x600")
root.iconbitmap("icon.ico")
root.resizable(True, True)
root.configure(padx=10, pady=10)
root.option_add("*Font", "calibri 12")
#Set the font for the Label widget
root.option_add("*Label.Font", "calibri 12 bold")

prompt_frame = tk.Frame(root)
prompt_frame.pack(fill="x", pady=(5, 5))
prompt_label = tk.Label(prompt_frame, text="Prompt:")
prompt_label.pack(side="left", padx=(0, 5))
prompt_send_icon = tk.PhotoImage(file='send.png')
prompt_send_button = ttk.Button(prompt_frame, image=prompt_send_icon, command=lambda:add_query(None))
prompt_send_button.pack(side="right")
prompt_entry = tk.Entry(prompt_frame)
prompt_entry.pack(fill="both", expand=True)
prompt_entry.bind("<FocusIn>", select_all_text)
prompt_entry.bind("<Return>", add_query)

response_label = tk.Label(root, text="Response:")
response_label.pack(anchor="w",  pady=(5, 5), padx=(0, 5))
response_textbox = tk.Text(root)
response_textbox.pack(fill="both", expand=True)


button_frame = tk.Frame(root)
button_frame.pack(pady=5)
submit_button = tk.Button(button_frame, text="Submit Query", command=lambda:add_query(None), width=20, height=2)
submit_button.pack(side="left", padx=10)
copy_button = tk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard, width=20, height=2)
copy_button.pack(side="right", padx=10)

root.mainloop()