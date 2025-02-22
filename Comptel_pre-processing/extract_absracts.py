import os
import fitz  # PyMuPDF

# Define the folder containing PDF files
pdf_folder = "ComputEL-8/sigdial/papers"  # Update this with your folder path
output_file = "Comptel_pre-processing/abstracts.txt"

# Function to extract the first paragraph (assumed abstract) from a PDF
def extract_abstract(pdf_path):
    try:
        doc = fitz.open(pdf_path)  # Open the PDF
        text = doc[0].get_text("text")  # Extract text from the first page
        paragraphs = text.split("\n\n")  # Split text into paragraphs
        
        if paragraphs:
            return paragraphs[0].strip()  # Return the first paragraph as abstract
        else:
            return "Abstract not found."
    
    except Exception as e:
        return f"Error extracting abstract: {e}"

# Scan the folder for PDFs and extract abstracts
with open(output_file, "w", encoding="utf-8") as out:
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            abstract = extract_abstract(pdf_path)
            out.write(f"{filename}:\n{abstract}\n\n")  # Save abstracts in the file

print(f"✅ Abstracts extracted and saved in {output_file}")