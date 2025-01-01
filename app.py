from flask import Flask, render_template, request, send_file, jsonify
import os
import subprocess
import tempfile
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Na początku pliku, po inicjalizacji aplikacji Flask
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def convert_key(ssh_key_path):
    logger.debug(f"Rozpoczęcie konwersji pliku: {ssh_key_path}")
    # Generowanie nazw plików tymczasowych
    pem_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.pem')
    ppk_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.ppk')
    
    try:
        # Konwersja do formatu PEM
        subprocess.run(['openssl', 'rsa', '-in', ssh_key_path, '-outform', 'PEM', '-out', pem_path], 
                      check=True, capture_output=True)
        
        # Konwersja do formatu PPK
        subprocess.run(['puttygen', pem_path, '-o', ppk_path, '-O', 'private'], 
                      check=True, capture_output=True)
        
        return ppk_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"Błąd konwersji: {e.stderr.decode()}")
    finally:
        # Czyszczenie plików tymczasowych
        if os.path.exists(pem_path):
            os.remove(pem_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    temp_input_path = None
    ppk_path = None  # Inicjalizacja zmiennej na początku funkcji
    
    if 'file' not in request.files:
        return jsonify({'error': 'Brak pliku'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nie wybrano pliku'}), 400
    
    try:
        # Zapisz przesłany plik
        filename = secure_filename(file.filename)
        temp_input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_input_path)
        
        # Konwertuj plik
        ppk_path = convert_key(temp_input_path)
        
        # Wyślij plik PPK
        return send_file(ppk_path, 
                        as_attachment=True,
                        download_name='converted.ppk',
                        mimetype='application/octet-stream')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Wyczyść pliki tymczasowe
        if temp_input_path and os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        if ppk_path and os.path.exists(ppk_path):
            os.remove(ppk_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 