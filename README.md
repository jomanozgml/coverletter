# Cover Letter Generator

[![License](https://img.shields.io/badge/License-Apache-blue.svg)](https://opensource.org/licenses/Apache-2)

## Overview

The Cover Letter Generator is a Python application that helps users generate cover letters for job applications based on their `resume` and a provided `job description`. It leverages the Google Generative AI model to create personalized cover letters.

## Features

- **Dynamic Content Generation:** Utilize the power of generative AI to dynamically create cover letters based on the user's resume and the given job description.

- **Job Description Analysis:** Automatically analyze the provided job description for key points and tailor the cover letter to address specific requirements.
  - For static webpage job extraction [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) library has been used.
  - For dynamic webpage job extraction [pyppeteer](https://pypi.org/project/pyppeteer/0.0.4/) library has been used.

- **User-Friendly Interface:** The application provides a simple and intuitive interface for users to input their resume, job description, and receive generated cover letters.

## Requirements

- Python 3.x
- Google Generative AI API Key (sign up at https://generativeai.dev/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cover-letter-generator.git
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
3. Set up your Google Generative AI API key in `.env` file
    - Obtain a Google Generative AI API key by signing up at https://generativeai.dev/.  
    - Create a .env file in the project's root directory:
    ``` ini
    API_KEY=your_actual_api_key_here
4. Copy and Paste Your Resume on `resume.txt` file located on root directory
5. Navigate to the root directory in command line and Run the application:
    ```bash
    python main.py
## Usage
1. Launch the application using the instructions in the Installation section.
2. Enter the job URL, load the job description, and load your resume.
3. Click the "Generate Cover Letter" button to create a personalized cover letter.
4. If not happy with the coverletter, write on prompt then hit enter to modify to your needs.
4. Press `Generate Coverletter` button to cpoy the generated cover letter to the clipboard.

## License
This project is licensed under the [Apache-2.0](https://opensource.org/licenses/Apache-2.0).

## Contributing
Feel free to contribute to the project. Please follow the Contributing Guidelines.

## Acknowledgments
Thanks to the Google Generative AI team for providing the powerful language model.

## Contact
*Email: [manoj.shrestha8080@gmail.com](mailto:manoj.shrestha8080@gmail.com)*