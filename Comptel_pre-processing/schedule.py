import pandas as pd
import yaml
import pdfplumber
from datetime import datetime, timedelta
import re

pdf_file = "Comptel_pre-processing/ComputEL-8 Schedule.pdf"
csv_file = "Comptel_pre-processing/Accepted_ComputEL-8_2025-02-22_1740228471.csv"
output_file = "Comptel_pre-processing/program.yml"

# Read CSV to create a mapping of paper titles to IDs
df = pd.read_csv(csv_file)
df = df[['id', 'title']].dropna()
title_to_id = {row['title'].strip(): row['id'] for _, row in df.iterrows()}

# Read PDF text
with pdfplumber.open(pdf_file) as pdf:
    text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

# Define the conference dates
base_date = datetime(2025, 3, 4)

# Process extracted text
lines = [line.strip() for line in text.split("\n") if line.strip()]

# Regex pattern to detect times and titles (handles variations in spacing)
time_pattern = re.compile(r"(\d{1,2}:\d{2})-(\d{1,2}:\d{2})\s+(.*)")

# Prepare the program structure
program = []
session = None
subsession = None

for line in lines:
    match = time_pattern.match(line)
    if match:
        start_str, end_str, title = match.groups()
        
        # Convert times to datetime
        try:
            start_time = datetime.strptime(start_str, "%H:%M")
            end_time = datetime.strptime(end_str, "%H:%M")
        except ValueError:
            continue  # Skip lines that don't match expected time format
        
        # Adjust date if necessary
        if start_time.hour < 6:  # Assume anything before 6 AM is for the next day
            base_date += timedelta(days=1)
        
        start_time = base_date.replace(hour=start_time.hour, minute=start_time.minute)
        end_time = base_date.replace(hour=end_time.hour, minute=end_time.minute)

        # Identify sessions, breaks, and talks
        if "BREAK" in title.upper():
            program.append({
                "title": "Break",
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S")
            })
        elif "SESSION" in title.upper() or "POSTER" in title.upper():
            if session:
                program.append(session)  # Save previous session
            
            session = {
                "title": title,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "subsessions": []
            }
        else:
            # Handle subsessions (papers)
            paper_id = title_to_id.get(title, None)
            subsession = {
                "title": title,
                "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "chair": "",
                "papers": []
            }
            if paper_id:
                subsession["papers"].append({
                    "id": int(paper_id),
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                })
            if session:
                session["subsessions"].append(subsession)

# Save last session
if session:
    program.append(session)

# Write YAML file
with open(output_file, "w") as f:
    yaml.dump(program, f, default_flow_style=False)

print(f"Program schedule successfully saved to {output_file}")