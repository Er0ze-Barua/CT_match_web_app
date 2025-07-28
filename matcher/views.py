import sys
import pandas as pd
import ast
import google.generativeai as genai
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
import numpy as np # Keep numpy for min() in sample_parsed_labels
import os
import csv
from django.http import HttpResponse
from .forms import CustomUserCreationForm


print("Python executable:", sys.executable)
# print("sys.path:", sys.path) # Removed: less critical for demo

# --- Define the EXACT 14 categories from doc_categories.txt description ---
MEDICAL_CATEGORIES_FOR_MATCHING = [
    "cancer", "cardiac", "endocrine", "gastrointestinal", "genetic",
    "healthy", "infection", "neurological", "other", "pediatric",
    "psychological", "pulmonary", "renal", "reproductive"
]

# --- Paths to your datasets from the ctmatch_ir set ---
DOC_TEXTS_PATH = r"C:\Users\imagi\Downloads\IBM FINAL\dataset\doc_texts.txt"
DOC_CATEGORIES_TXT_PATH = r"C:\Users\imagi\Downloads\IBM FINAL\dataset\doc_categories.txt"
INDEX2DOCID_TXT_PATH = r"C:\Users\imagi\Downloads\IBM FINAL\dataset\index2docid.txt"

# --- Global DataFrame for clinical trials, loaded once on server startup ---
trial_df = pd.DataFrame()

try:
    print("\n--- INFO: Loading CTMatch IR Dataset Components ---") # Changed DEBUG to INFO for general clarity

    with open(DOC_TEXTS_PATH, 'r', encoding='utf-8') as f:
        doc_texts = [line.strip() for line in f if line.strip()]
    # print(f"DEBUG: Loaded {len(doc_texts)} documents from doc_texts.txt") # Removed: less critical for demo

    with open(DOC_CATEGORIES_TXT_PATH, 'r', encoding='utf-8') as f:
        category_lines = [line.strip() for line in f if line.strip()]
    # print(f"DEBUG: Loaded {len(category_lines)} category vectors from doc_categories.txt") # Removed

    with open(INDEX2DOCID_TXT_PATH, 'r', encoding='utf-8') as f:
        doc_ids = [line.strip() for line in f if line.strip()]
    # print(f"DEBUG: Loaded {len(doc_ids)} document IDs from index2docid.txt") # Removed

    if not (len(doc_texts) == len(category_lines) == len(doc_ids)):
        raise ValueError("Mismatch in number of lines across doc_texts.txt, doc_categories.txt, and index2docid.txt!")

    processed_categories = []
    CATEGORY_THRESHOLD = 0.1
    for i, line in enumerate(category_lines):
        try:
            probabilities = [float(p) for p in line.split(',')]
            current_trial_categories = []
            for j, prob in enumerate(probabilities):
                if prob > CATEGORY_THRESHOLD:
                    current_trial_categories.append(MEDICAL_CATEGORIES_FOR_MATCHING[j])
            processed_categories.append(current_trial_categories)
        except (ValueError, IndexError) as e:
            print(f"Warning: Skipping malformed line {i+1} in doc_categories.txt: {line}. Error: {e}")
            processed_categories.append([])

    trial_df = pd.DataFrame({
        'trial_id': doc_ids,
        'doc': doc_texts,
        'parsed_labels': processed_categories
    })
    print("INFO: Successfully created trial_df from dataset components.") # Changed DEBUG to INFO

    print("\n--- INFO: Trial Data Summary ---") # Changed DEBUG to INFO
    print("First 5 entries of 'trial_df':")
    print(trial_df[['trial_id', 'doc', 'parsed_labels']].head())
    print("Total rows in 'trial_df':", len(trial_df))
    # print("Type of first element in 'parsed_labels' column:", type(trial_df['parsed_labels'].iloc[0])) # Removed
    print("--- END INFO: Trial Data Summary ---\n")

except FileNotFoundError as e:
    print(f"CRITICAL ERROR: Required dataset file not found: {e}. Please check your paths.")
    trial_df = pd.DataFrame()
except ValueError as e:
    print(f"CRITICAL ERROR: Data processing issue during startup: {e}")
    trial_df = pd.DataFrame()
except Exception as e:
    print(f"CRITICAL ERROR: An unexpected error occurred during trial data loading: {e}")
    import traceback
    traceback.print_exc()
    trial_df = pd.DataFrame()


# --- Configure Gemini API ---
genai.configure(api_key="") # REPLACE WITH YOUR ACTUAL API KEY
model = genai.GenerativeModel("gemini-1.5-pro")


# --- Authentication Views ---
def login_view(request):
    if request.method == "POST":
        print("Login view reached! (POST)") # Kept for demo: shows request type
        username = request.POST.get("username")
        # password = request.POST.get("password") # Removed: sensitive info
        # print(f"DEBUG: Username: {username}, Password: {password}") # Removed: sensitive info
        user = authenticate(request, username=username, password=request.POST.get("password")) # Access password directly here
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "matcher/login.html", {"error": "Invalid credentials"})
    return render(request, "matcher/login.html")

# --- REGISTER VIEW ---
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST) # <--- USE YOUR CUSTOM FORM HERE
        if form.is_valid():
            user = form.save() # Saves the new user to the database
            # Ensure email is saved directly by form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm() # <--- USE YOUR CUSTOM FORM HERE for GET requests

    return render(request, 'matcher/register.html', {'form': form})

# --- LOGOUT VIEW ---
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# --- FORGOT PASSWORD VIEW ---
def forgot_password_view(request):
    # This view now just redirects to Django's built-in password reset form
    return redirect('password_reset')

# --- UPDATE EMAIL VIEW ---
@login_required(login_url='/')
def update_email_view(request):
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        current_password = request.POST.get('current_password')
        user = request.user

        if not new_email or not current_password:
            messages.error(request, "Both new email and current password are required.")
            return redirect('home')

        if not user.check_password(current_password):
            messages.error(request, "Incorrect current password.")
            return redirect('home')

        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, "This email address is already in use by another account.")
            return redirect('home')

        user.email = new_email
        user.save()
        messages.success(request, "Your email address has been updated successfully!")
        return redirect('home')
    else:
        return redirect('home')

# --- Home and Results View (Version A - NO Age/Gender, NO Pagination) ---
@login_required(login_url='/')
def home_view(request):
    if request.method == "POST":
        patient_input = request.POST.get("patient_description")

        print("🟢 Received input:", patient_input) # Kept for demo: shows patient input

        prompt_categories_str = str(MEDICAL_CATEGORIES_FOR_MATCHING)
        prompt = f"""
        Given the following patient description, return a list of relevant medical labels/categories from this list:
        {prompt_categories_str}.

        Respond in this format:
        Labels: ['label1', 'label2', ...]

        Patient Description: {patient_input}
        """

        try:
            print("🟢 Sending prompt to Gemini...") # Kept for demo
            response = model.generate_content(prompt)
            content = response.text
            print("🟢 Gemini response:", content) # Kept for demo: shows raw Gemini response
            
            label_line = [line for line in content.splitlines() if "Labels:" in line]
            if not label_line:
                print("Warning: Gemini response did not contain 'Labels:' line. Attempting direct parse.")
                if content.strip().startswith('[') and content.strip().endswith(']'):
                    labels = ast.literal_eval(content.strip())
                else:
                    labels = []
            else:
                label_list_str = label_line[0].split("Labels:")[-1].strip()
                labels = ast.literal_eval(label_list_str)
            print("🟢 Extracted labels (from Gemini):", labels) # Kept for demo: shows final extracted labels
            # print("DEBUG: Type of extracted labels:", type(labels)) # Removed: too verbose

            print("\n--- INFO: Matching Logic ---") # Changed DEBUG to INFO
            print("Labels from Gemini for matching:", labels) # Kept for demo
            # print("Sample of DataFrame's 'parsed_labels' column for comparison:") # Removed: too verbose
            if not trial_df.empty:
                # sample_parsed_labels = trial_df['parsed_labels'].sample(min(5, len(trial_df)), random_state=42).tolist() # Removed: too verbose
                # print(sample_parsed_labels) # Removed
                pass # Placeholder for removed debug lines
            else:
                print("INFO: trial_df is empty, no matching possible.") # Changed DEBUG to INFO

            if not trial_df.empty:
                matched_trials = trial_df[trial_df['parsed_labels'].apply(
                    lambda trial_labels: any(label in trial_labels for label in labels)
                )]
            else:
                matched_trials = pd.DataFrame()

            print("INFO: Number of matched trials FOUND:", len(matched_trials)) # Changed DEBUG to INFO, crucial metric
            if not matched_trials.empty:
                print("INFO: First 5 matched trials:") # Changed DEBUG to INFO
                print(matched_trials[['trial_id', 'doc', 'parsed_labels']].head()) # Kept for demo: shows sample matches
            print("--- END INFO: Matching Logic ---\n")

            request.session['download_trial_ids'] = matched_trials['trial_id'].tolist()
            request.session['download_patient_input'] = patient_input
            request.session['download_predicted_labels'] = labels

            return render(request, "matcher/results.html", {
                "patient_input": patient_input,
                "predicted_labels": labels,
                "matching_trials": matched_trials.head(15).to_dict(orient="records"),
            })

        except Exception as e:
            print(f"🔴 An error occurred in home_view POST: {e}")
            messages.error(request, f"An error occurred: {e}")
            return render(request, "matcher/results.html", {
                "error": str(e),
                "patient_input": patient_input
            })

    return render(request, "matcher/home.html")

# --- Download Results View ---
@login_required(login_url='/')
def download_results(request):
    download_trial_ids = request.session.get('download_trial_ids', [])
    download_patient_input = request.session.get('download_patient_input', 'N/A')
    download_predicted_labels = request.session.get('download_predicted_labels', [])

    trials_for_download = trial_df[trial_df['trial_id'].isin(download_trial_ids)]
    trials_for_download = trials_for_download.head(50)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clinical_trials_output.csv"'
    writer = csv.writer(response)

    writer.writerow(['AI Clinical Trial Eligibility Assessment Output'])
    writer.writerow([])
    writer.writerow(['Patient Description:'])
    writer.writerow([download_patient_input])
    writer.writerow([])
    writer.writerow(['Conditions Detected:'])
    writer.writerow([', '.join(download_predicted_labels)])
    writer.writerow([])
    writer.writerow(['Matching Trials (Top 50):'])
    csv_columns = ['trial_id', 'doc', 'parsed_labels']
    writer.writerow(csv_columns)

    for trial in trials_for_download.to_dict(orient='records'):
        row = [
            trial.get('trial_id', ''),
            trial.get('doc', ''),
            ', '.join(trial.get('parsed_labels', [])),
        ]
        writer.writerow(row)

    return response