import os
import requests
import json
from flask import Flask, request, render_template, jsonify
import PyPDF2

app = Flask(__name__)

# Para pegar a chave da variável de ambiente (defini no Render como GEMINI_API_KEY)
API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"


def generate_response_with_ai(email_text):
    """
    Usa a API do Gemini para sugerir resposta e classificar o e-mail.
    Retorna (dict, status_code).
    """
    if not API_KEY:
        return {"error": "API_KEY não está configurada."}, 401

    system_prompt = (
        "Você é um assistente de e-mail. Sua tarefa é analisar o conteúdo de um e-mail. "
    "Primeiro, determine se o e-mail é 'Produtivo' (requer ação ou resposta) "
    "ou 'Improdutivo' (não requer ação imediata). "
    "Em seguida, crie uma resposta profissional apropriada para a categoria. "
    "A resposta deve começar chamando o remetente pelo nome, se disponível no e-mail. "
    "Finalize sempre com uma saudação de despedida e um agradecimento, mencionando o nome da empresa ou pessoa que enviou. "
    "A saída deve ser um objeto JSON válido no formato: "
    "{\"categoria\": \"Categoria do email\", \"resposta\": \"Resposta sugerida\"}."
    )

    payload = {
        "contents": [{"parts": [{"text": f"Email para analisar:\n\n{email_text}"}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "categoria": {"type": "STRING"},
                    "resposta": {"type": "STRING"},
                },
            },
        },
    }

    try:
        response = requests.post(
            f"{API_URL}?key={API_KEY}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        raw_json_string = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "{}")
        )

        return json.loads(raw_json_string), 200

    except requests.exceptions.HTTPError as err:
        text = ""
        try:
            text = err.response.text
        except Exception:
            text = str(err)
        return {"error": f"Erro HTTP: {text}"}, getattr(err.response, "status_code", 500)
    except json.JSONDecodeError:
        return {"error": "Resposta da IA não é um JSON válido."}, 500
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/classificador")
def classificador():
    return render_template("index.html")


@app.route("/processar", methods=["POST"])
def processar():
    email_text = ""
    # Texto direto
    if "email_text" in request.form and request.form["email_text"]:
        email_text = request.form["email_text"]
    # Arquivo enviado
    elif "email_file" in request.files and request.files["email_file"].filename != "":
        file = request.files["email_file"]
        filename = file.filename.lower()
        try:
            if filename.endswith(".txt"):
                email_text = file.read().decode("utf-8", errors="ignore")
            elif filename.endswith(".pdf"):
                reader = PyPDF2.PdfReader(file)
                email_text = ""
                for page in reader.pages:
                    email_text += page.extract_text() or ""
            else:
                return jsonify({"error": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
        except Exception as e:
            return jsonify({"error": f"Erro ao ler o arquivo: {str(e)}"}), 500
    else:
        return jsonify({"error": "Nenhum texto de e-mail ou arquivo fornecido."}), 400

    # Gera resposta e a classificação viapelo Gemini
    result, status_code = generate_response_with_ai(email_text)
    if status_code != 200:
        return jsonify(result), status_code
    return jsonify(result)


if __name__ == "__main__":
    # para teste local
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
