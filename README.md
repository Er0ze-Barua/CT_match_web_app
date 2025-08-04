# AI-Powered Clinical Trial Matching Web App

An intelligent web application that uses Google's Gemini API to classify a patient's condition from a text-based description and matches them with relevant clinical trials from a comprehensive dataset.

## Core Features

Intelligent Patient Classification: Utilizes the Gemini 1.5 Pro API to analyze a patient's text-based description and classify it into one or more of 14 predefined medical categories (e.g., cardiac, pulmonary, neurological).

Clinical Trial Matching Engine: A robust backend system built with Python and Pandas that filters a dataset of over 370,000 trials. Trials are matched based on shared medical categories with the patient's condition.

Secure User Authentication: A complete and secure user management system including user registration (with email), login, and a password reset flow.

Data Visualization & Export: Displays matched trials in a clean, user-friendly table and provides the option to download the top 50 relevant trials as a CSV file.

Aesthetic & Responsive Design: Features a consistent, dark-themed UI with sleek hover effects and a single-box, centered layout that adapts gracefully to different screen sizes.

## Technologies Used

Backend: Python, Django

AI/ML: Google Gemini 1.5 Pro API

Data Science: Pandas

Database: SQLite3 (for development)

Frontend: HTML, CSS, JavaScript (for password validation)

## Evaluation & Performance

The system's performance was measured using a two-part automated evaluation on a dataset of 140 test cases:

Gemini's Classification Accuracy: A measure of how accurately the API classifies patient descriptions. The system achieved a 93.57% accuracy score.

System Retrieval Relevance: A measure of the quality of the matched trials using the Jaccard Index. The system achieved a solid average Jaccard Index of 0.41.

## Setup and Installation

This project is built on Python 3.12 and Django 5.2.4.

Clone the repository:
git clone https://github.com/Er0ze-Barua/CT_match_web_app.git

Navigate to the project directory:
cd CT_match_web_app

Create a virtual environment and activate it:
python -m venv venv
.\venv\Scripts\activate (on Windows)

Install project dependencies:
pip install -r requirements.txt

Set up the database:
python manage.py makemigrations
python manage.py migrate

Create a superuser:
python manage.py createsuperuser

Run the development server:
python manage.py runserver