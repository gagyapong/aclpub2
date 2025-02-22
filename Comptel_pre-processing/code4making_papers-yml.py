import pandas as pd
import yaml

# Define file paths (update these paths with your actual file locations)
submission_csv = "Comptel_pre-processing/submission (1).csv"
author_csv = "Comptel_pre-processing/author.csv"
yaml_output = "Comptel_pre-processing/pps.yml"

# Load CSV files with encoding fix
submission_df = pd.read_csv(submission_csv, encoding="utf-8")
author_df = pd.read_csv(author_csv, encoding="ISO-8859-1")  # Fix encoding issue

# Normalize column names (strip spaces, lowercase them)
submission_df.columns = submission_df.columns.str.lower().str.strip()
author_df.columns = author_df.columns.str.lower().str.strip()

# Define expected columns for extraction
submission_columns = ["abstract", "paper_type", "presentation_type", "id", "title"]
author_columns = ["email", "first_name", "instituition", "last_name"]

# Check if all required columns exist
missing_submission_cols = [col for col in submission_columns if col not in submission_df.columns]
missing_author_cols = [col for col in author_columns if col not in author_df.columns]

if missing_submission_cols:
    raise ValueError(f"Missing columns in submission CSV: {missing_submission_cols}")
if missing_author_cols:
    raise ValueError(f"Missing columns in author CSV: {missing_author_cols}")

# Merge author and submission data on "id" (without duplicating papers)
merged_df = submission_df.merge(author_df, on="id", how="left")

# Group authors by paper ID
grouped_authors = merged_df.groupby("id").apply(lambda g: [
    {
        "email": row["email"],
        "first_name": row["first_name"],
        "instituition": row["instituition"],
        "last_name": row["last_name"]
    }
    for _, row in g.iterrows()
]).to_dict()

# Create YAML structure
entries = []
for _, row in submission_df.iterrows():
    paper_id = row["id"]
    paper_entry = {
        "abstract": row["abstract"] if pd.notna(row["abstract"]) else "",
        "attributes": {
            "paper_type": row["paper_type"],
            "presentation_type": row["presentation_type"],
        },
        "authors": grouped_authors.get(paper_id, []),  # Fetch authors for this paper ID
        "file": f"{paper_id}.pdf",  # Assigning [id].pdf as the file name
        "id": int(paper_id),
        "title": row["title"],
    }
    entries.append(paper_entry)

# Save to a YAML file
with open(yaml_output, "w", encoding="utf-8") as file:
    yaml.dump(entries, file, allow_unicode=True, default_flow_style=False)

print(f"✅ YAML file successfully created: {yaml_output}")