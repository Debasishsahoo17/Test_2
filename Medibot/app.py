from flask import Flask, jsonify, request
from flask_cors import CORS
from docx import Document

app = Flask(__name__)
CORS(app)
1
# Function to extract disease data from Word file
def fetch_disease_data_from_word(file_path):
    document = Document(file_path)
    disease_data = []
    diseases = document.paragraphs

    current_disease = None
    for para in diseases:
        text = para.text.strip()

        if text.startswith("Disease:"):
            if current_disease:
                disease_data.append(current_disease)
            current_disease = {"name": text.replace("Disease:", "").strip()}
        elif "Symptoms" in text:
            current_disease["symptoms"] = text.replace("Symptoms:", "").split(", ")
        elif "Prevention and cure" in text or "Prevention:" in text:
            current_disease["prevention"] = text.replace("Prevention and cure:", "").replace("Prevention:", "").split(", ")
        elif "Medicine:" in text or "Medications:" in text:
            current_disease["medications"] = text.replace("Medicine:", "").replace("Medications:", "").split(", ")
        elif "Remedies" in text or "Treatment:" in text:
            current_disease["home_remedies"] = text.replace("Treatment:", "").replace("Remedies:", "").split(", ")

    if current_disease:
        disease_data.append(current_disease)

    return disease_data

@app.route('/diseases', methods=['GET'])
def list_diseases():
    disease_data = fetch_disease_data_from_word("disease_symptoms.docx")
    return jsonify({"diseases": [d["name"] for d in disease_data]})

@app.route('/disease/<string:name>', methods=['GET'])
def get_disease(name):
    disease_data = fetch_disease_data_from_word("disease_symptoms.docx")
    for disease in disease_data:
        if disease["name"].lower() == name.lower():
            return jsonify(disease)
    return jsonify({"error": "Disease not found"}), 404

@app.route('/symptoms', methods=['POST'])
def find_diseases_by_symptoms():
    symptoms = request.json.get("symptoms", [])
    disease_data = fetch_disease_data_from_word("disease_symptoms.docx")
    matched_diseases = []
    for disease in disease_data:
        if any(symptom.lower() in map(str.lower, disease.get("symptoms", [])) for symptom in symptoms):
            matched_diseases.append(disease["name"])
    return jsonify({"matched_diseases": matched_diseases})

if __name__ == '__main__':
    app.run(debug=True)
