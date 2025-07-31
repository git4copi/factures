import os
import json
import base64
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import tempfile
import shutil
from pdf_processor import PDFProcessor
from excel_processor import ExcelProcessor
from azure_ai_processor import AzureAIProcessor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['IMAGES_FOLDER'] = 'images'
app.config['OUTPUT_FOLDER'] = 'output'

# Créer les dossiers nécessaires
for folder in [app.config['UPLOAD_FOLDER'], app.config['IMAGES_FOLDER'], app.config['OUTPUT_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Initialiser les processeurs
pdf_processor = PDFProcessor()
excel_processor = ExcelProcessor()
azure_processor = AzureAIProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'pdf_file' not in request.files or 'excel_file' not in request.files:
            return jsonify({'error': 'PDF et Excel requis'}), 400
        
        pdf_file = request.files['pdf_file']
        excel_file = request.files['excel_file']
        
        if pdf_file.filename == '' or excel_file.filename == '':
            return jsonify({'error': 'Fichiers non sélectionnés'}), 400
        
        # Sauvegarder les fichiers
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(pdf_file.filename))
        excel_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(excel_file.filename))
        
        pdf_file.save(pdf_path)
        excel_file.save(excel_path)
        
        return jsonify({
            'message': 'Fichiers uploadés avec succès',
            'pdf_path': pdf_path,
            'excel_path': excel_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process_files():
    try:
        data = request.get_json()
        pdf_path = data.get('pdf_path')
        excel_path = data.get('excel_path')
        prompt = data.get('prompt', 'Analysez cette image et extrayez les informations importantes')
        
        if not pdf_path or not excel_path:
            return jsonify({'error': 'Chemins des fichiers manquants'}), 400
        
        # 1. Convertir PDF en images
        images_info = pdf_processor.convert_pdf_to_images(pdf_path, app.config['IMAGES_FOLDER'])
        
        # 2. Traiter chaque image avec Azure AI
        results = []
        for image_info in images_info:
            image_path = image_info['path']
            page_num = image_info['page']
            
            # Analyser l'image avec Azure AI
            ai_result = azure_processor.analyze_image(image_path, prompt)
            
            results.append({
                'page': page_num,
                'image_path': image_path,
                'ai_result': ai_result
            })
        
        # 3. Mettre à jour le fichier Excel
        output_excel_path = os.path.join(app.config['OUTPUT_FOLDER'], 'resultat_traite.xlsx')
        excel_processor.update_excel_with_results(excel_path, results, output_excel_path)
        
        return jsonify({
            'message': 'Traitement terminé avec succès',
            'results': results,
            'output_excel': output_excel_path
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['IMAGES_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 