import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from page_parser import *
from pyppeteer_check import *
import asyncio
import webbrowser
import os
import google.generativeai as genai
from datetime import datetime
from markdown_pdf import MarkdownPdf, Section

# Read environment variables from .env file
with open('.env', 'r') as env_file:
    for line in env_file:
        key, value = line.strip().split('=')
        os.environ[key] = value

genai.configure(api_key=os.getenv('API_KEY'))

# Set up the model
generation_config = {
  "temperature": 0.4,
  "top_p": 0.7,
  "top_k": 40,
  "max_output_tokens": 2048,
}

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config)

chat = model.start_chat(history=[])

class CollapsibleFrame(tk.Frame):
    def __init__(self, parent, text="", *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.show = tk.BooleanVar(value=True)

        # Title frame with button
        self.title_frame = tk.Frame(self)
        self.title_frame.pack(fill="x")

        # Toggle button
        self.toggle_button = tk.Button(self.title_frame, text=" ▼ ", width=2, command=self.toggle)
        self.toggle_button.pack(side="left")

        # Title label
        self.title_label = tk.Label(self.title_frame, text=text, font="calibri 12 bold")
        self.title_label.pack(side="left", padx=5)

        # Container for the collapsible content
        self.sub_frame = tk.Frame(self)
        self.sub_frame.pack(fill="both", expand=True)

    def toggle(self):
        if self.show.get():
            self.sub_frame.pack_forget()
            self.toggle_button.configure(text=" ▶ ")
        else:
            self.sub_frame.pack(fill="both", expand=True)
            self.toggle_button.configure(text=" ▼ ")
        self.show.set(not self.show.get())

def new_fetch_vacancy(event):
    vacancy_url = url_textbox.get()
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
    file_path = filedialog.askopenfilename(
        initialdir=".",
        title="Select Resume File",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    if file_path:
        try:
            with open(file_path, 'r') as file:
                resume_textbox.delete("1.0", tk.END)
                resume_textbox.insert(tk.END, file.read())
        except Exception as e:
            messagebox.showerror("Error", f"Error loading resume: {str(e)}")

# Function to load template cover letter via file dialog
def load_template():
    global template_content
    file_path = filedialog.askopenfilename(
        initialdir=".",
        title="Select Template File",
        filetypes=(("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*"))
    )
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                template_var.set(True)
                if template_var.get():
                    cover_letter_textbox.delete('1.0', tk.END)
                    cover_letter_textbox.insert(tk.END, template_content)
                else:
                    cover_letter_textbox.delete('1.0', tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading template: {str(e)}")

company_name = ""

def convert_cover_letter_to_pdf():
    if not company_name:
        messagebox.showwarning("Warning", "Company name not available.")
        return
    markdown_content = cover_letter_textbox.get("1.0", tk.END)
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"1_Coverletter_{current_date}_{company_name}.pdf"
    pdf = MarkdownPdf()
    pdf.add_section(Section(markdown_content), user_css="body {text-align: justify;}")
    pdf.save(f"coverletters/{filename}")
    # Show success message
    messagebox.showinfo("Success", f"Cover letter saved as {filename}")
    # Open the folder containing the PDF
    os.startfile("coverletters")

def submit_form():
    global company_name
    jd_text = jd_textbox.get("1.0", "end-1c")
    resume_text = resume_textbox.get("1.0", "end-1c")

    if url_textbox.get() == "":
        messagebox.showwarning("Warning", "Please provide URL")
        return
    if jd_text == "":
        messagebox.showwarning("Warning", "Please load Job Description")
        return
    if resume_text == "":
        messagebox.showwarning("Warning", "Please provide Resume")
        return


    details_prompt = f"""From this job description and resume, extract:
    1. Company name
    2. Job title
    3. Hiring manager name (if mentioned, otherwise respond with 'Hiring Manager')
    4. Applicant name
    5. Applicant email
    6. Applicant phone number

    Format your response in exactly six lines:
    First line: company name
    Second line: job title
    Third line: hiring manager name
    Fourth line: applicant name
    Fifth line: applicant email
    Sixth line: applicant phone number

    Job description: {jd_text}
    Resume: {resume_text}"""

    details_response = chat.send_message(details_prompt)

    details_lines = details_response.text.strip().split('\n')
    company_name = details_lines[0].strip()
    job_title = details_lines[1].strip()
    hiring_manager = details_lines[2].strip()
    name = details_lines[3].strip()
    email = details_lines[4].strip()
    phone = details_lines[5].strip()
    current_date = datetime.now().strftime("%B %d, %Y")

    if template_var.get():
        message = [ f"""Write full cover letter by replacing the placeholders in the template
            (retain the markdown syntax) with the following details:
            Date: {current_date}
            Company name: {company_name}
            Job title: {job_title}
            Hiring manager: {hiring_manager}
            in the template provided below:
            {template_content}"""]

    else:
        message = [
            f"""Generate a cover letter using the following details:
            Date: {current_date}
            Company name: {company_name}
            Job title: {job_title}
            Hiring manager: {hiring_manager}
            Job description: {jd_text}
            Resume: {resume_text}

            0. Use this format for the cover letter:
                Date: {current_date}
                To,
                {hiring_manager},
                {company_name}
                ...
                ...
                Best Regards,
                {name}
                {email}
                {phone}
            1. Addresses the key requirements from the job description
            2. Highlights relevant experience from the resume
            3. Shows enthusiasm for the role at {company_name} for the {job_title} position
            4. Maintains a professional yet conversational tone
            5. Bold out the key points and words
            The content should fit naturally into a professional cover letter format."""
        ]

    generate_content(message)

def generate_content(message):
    # Disable the button during processing
    submit_button.config(state="disabled")
    copy_button.config(state="disabled")
    save_pdf_button.config(state="disabled")
    # Display processing message
    cover_letter_textbox.delete("1.0", "end")
    cover_letter_textbox.insert("1.0", "\n\nProcessing...")

    # Center the text
    cover_letter_textbox.tag_configure("center", justify="center", font=("calibri", 24))
    cover_letter_textbox.tag_add("center", "1.0", "end")

    # Update the GUI to show the processing message
    root.update_idletasks()

    # response = model.generate_content(prompt_parts)
    response = chat.send_message(message)
    cover_letter_textbox.delete("1.0", "end")
    cover_letter_textbox.insert("1.0", response.text)

    # Enable the button after processing is complete
    submit_button.config(state="normal")
    copy_button.config(state="normal")
    save_pdf_button.config(state="normal")
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
root.geometry("600x800")
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
url_textbox.bind("<Return>", new_fetch_vacancy)

jd_collapsible = CollapsibleFrame(root, text="Job Description")
jd_collapsible.pack(fill="x", pady=(0, 5))
jd_frame = tk.Frame(jd_collapsible.sub_frame)
jd_frame.pack(fill="x", pady=(0, 5))
load_jd_button = tk.Button(jd_frame, text="Load Job Description", command=lambda:new_fetch_vacancy(None))
load_jd_button.pack(side="left")

# Checkbox to indicate whether the JD contains specified keywords
checkbox_var = tk.BooleanVar()
citizenship_checkbox = tk.Checkbutton(jd_frame, text="Citizenship", variable=checkbox_var)
citizenship_checkbox.pack(side="left", padx=(25, 0))

jd_textbox = tk.Text(jd_collapsible.sub_frame, height=6, wrap="word")
jd_textbox.pack(fill="both", expand=True, pady=(5, 0))

resume_collapsible = CollapsibleFrame(root, text="Resume")
resume_collapsible.pack(fill="x", pady=(0, 5))
resume_frame = tk.Frame(resume_collapsible.sub_frame)
resume_frame.pack(fill="x", pady=(5, 5))
load_resume_button = tk.Button(resume_frame, text="Load Resume", command=load_resume)
load_resume_button.pack(side="left")

resume_textbox = tk.Text(resume_collapsible.sub_frame, height=4, wrap="word")
resume_textbox.pack(fill="both", expand=True)

coverletter_collapsible = CollapsibleFrame(root, text="Cover Letter")
coverletter_collapsible.pack(fill="both", expand=True, pady=(0, 5))
cover_letter_frame = tk.Frame(coverletter_collapsible.sub_frame)
cover_letter_frame.pack(fill="x", pady=(5, 5))
template_var = tk.BooleanVar()
template_check = tk.Checkbutton(cover_letter_frame, text="Use Template", variable=template_var)
template_check.pack(side="left")
load_template_button = tk.Button(cover_letter_frame, text="Load Template", command=load_template)
load_template_button.pack(side="left")
cover_letter_textbox = tk.Text(coverletter_collapsible.sub_frame, height=8, wrap="word")
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
copy_button.pack(side="left", padx=10)
save_pdf_button = tk.Button(button_frame, text="Save as PDF", command=convert_cover_letter_to_pdf, width=20, height=2)
save_pdf_button.pack(side="left", padx=10)

root.mainloop()