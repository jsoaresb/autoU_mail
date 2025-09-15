import os
import requests
import json
from flask import Flask, request, render_template, jsonify
from transformers import pipeline
import PyPDF2

app = Flask(__name__)

# Configuração da API do Gemini
API_KEY = "AIzaSyBQsCqUIOZuk81U1kcA_B2TdNghAkLChEk"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

# Inicializa o pipeline de NLP para análise de sentimento.
# Este pipeline será usado para classificar os emails.
# O modelo 'distilbert-base-uncased-finetuned-sst-2-english' é um classificador de sentimento.
# Vamos usá-lo para determinar se o email é 'Produtivo' ou 'Improdutivo'.
classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def classify_email(text):
    """
    Classifica o email como 'Produtivo' ou 'Improdutivo' com base no sentimento.
    A classificação se baseia em uma interpretação do sentimento:
    - POSITIVE: Produtivo (bom para negócios)
    - NEGATIVE: Improdutivo (não requer ação)
    """
    result = classifier(text)[0]
    if result['label'] == 'POSITIVE':
        return 'Produtivo'
    else:
        return 'Improdutivo'

def generate_response_with_ai(email_text):
    """
    Usa a API do Gemini para sugerir uma resposta para o email.
    """
    if not API_KEY:
        return {"error": "API_KEY não está configurada."}, 401
    
    # Prompt para a IA
    # A instrução para o modelo é clara: classificar e gerar uma resposta em português
    system_prompt = "Você é um assistente de e-mail. Sua tarefa é analisar o conteúdo de um e-mail. Primeiro, determine se o e-mail é 'Produtivo' (requer ação ou resposta) ou 'Improdutivo' (não requer ação imediata, como agradecimentos ou mensagens gerais). Em seguida, crie uma resposta curta e profissional que seja apropriada para a categoria. A saída deve ser um objeto JSON no formato: {'categoria': 'Categoria do email', 'resposta': 'Resposta sugerida'}."
    
    payload = {
        "contents": [{"parts": [{"text": f"Email para analisar:\n\n{email_text}"}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "categoria": {"type": "STRING"},
                    "resposta": {"type": "STRING"}
                }
            }
        }
    }

    try:
        response = requests.post(
            f"{API_URL}?key={API_KEY}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        response.raise_for_status()
        
        # A API do Gemini retorna a resposta dentro de uma string de texto JSON
        data = response.json()
        raw_json_string = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
        
        # Faz o parse da string JSON para um objeto Python
        return json.loads(raw_json_string), 200

    except requests.exceptions.HTTPError as err:
        return {"error": f"Erro HTTP: {err.response.text}"}, err.response.status_code
    except json.JSONDecodeError:
        return {"error": "Resposta da IA não é um JSON válido."}, 500
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/classificador')
def classificador():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    email_text = ""
    if 'email_text' in request.form and request.form['email_text']:
        email_text = request.form['email_text']
    elif 'email_file' in request.files and request.files['email_file'].filename != '':
        file = request.files['email_file']
        
        # Verifica a extensão do arquivo para ler o conteúdo corretamente
        if file.filename.endswith('.txt'):
            email_text = file.read().decode('utf-8')
        elif file.filename.endswith('.pdf'):
            reader = PyPDF2.PdfReader(file)
            email_text = ""
            for page in reader.pages:
                email_text += page.extract_text() or ""
        else:
            return jsonify({"error": "Formato de arquivo não suportado. Por favor, use .txt ou .pdf."}), 400
    else:
        return jsonify({"error": "Nenhum texto de e-mail ou arquivo fornecido."}), 400

    # Chamada para a nova função com IA
    result, status_code = generate_response_with_ai(email_text)
    
    if status_code != 200:
        return jsonify(result), status_code
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)