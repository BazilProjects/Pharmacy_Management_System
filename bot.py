import spacy
import PyPDF2
import csv

# Load spaCy's pre-trained model
nlp = spacy.load("en_core_web_sm")  # Use a smaller model

# Function to read text from a .pdf file
def read_pdf(file_path):
    text = []
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text.append(page.extract_text())
    return text

# Extract entities using spaCy
def extract_information(sentences):
    extracted_data = []

    for sentence in sentences:
        doc = nlp(sentence)
        diseases = []
        symptoms = []
        tests = []
        drugs = []
        prescriptions = []

        for ent in doc.ents:
            if ent.label_ == "DISEASE":  # Customize based on your model and labels
                diseases.append(ent.text)
            elif ent.label_ == "SYMPTOM":  # Customize based on your model and labels
                symptoms.append(ent.text)
            # Add more conditions for other entity types...
            # Example:
            elif ent.label_ == "TEST":
                tests.append(ent.text)
            elif ent.label_ == "DRUG":
                drugs.append(ent.text)
            elif ent.label_ == "PRESCRIPTION":
                prescriptions.append(ent.text)

        extracted_data.append({
            'Disease': ', '.join(diseases),
            'Symptom': ', '.join(symptoms),
            'Test': ', '.join(tests),
            'Drug': ', '.join(drugs),
            'Prescription': ', '.join(prescriptions),
        })

    return extracted_data

# Define the write_to_csv function
def write_to_csv(data, filename):
    # Specify the CSV fieldnames based on the keys of the first dictionary in data
    fieldnames = data[0].keys()
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()  # Write the header
        for row in data:
            writer.writerow(row)  # Write each row of data

# File path to your Uganda Clinical Guidelines .pdf file
file_path = '/home/omenyo/Pictures/Uganda Clinical Guidelines 2023.pdf'

# Read the .pdf file
sentences = read_pdf(file_path)

# Filter out None or empty sentences
sentences = [sentence for sentence in sentences if sentence]  # Remove empty text

# Extract information from sentences
extracted_data = extract_information(sentences)

# Write extracted data to CSV
write_to_csv(extracted_data, 'extracted_guidelines.csv')

print("Data extraction complete. Check 'extracted_guidelines.csv'.")
