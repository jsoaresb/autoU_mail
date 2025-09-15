AutoU Mail – Classificação e Resposta Automática de E-mails

Projeto desenvolvido como desafio para automatizar a classificação e resposta de e-mails usando Inteligência Artificial através da API Google Gemini.

 Funcionalidades

 Upload de arquivos .txt ou .pdf com conteúdo de e-mail.

⌨️ Inserção direta de texto para análise sem necessidade de upload.

🤖 Classificação automática dos e-mails em duas categorias:

Produtivo → requer ação ou resposta.

Improdutivo → não requer resposta imediata.

📨 Sugestão de resposta automática adaptada ao tipo de e-mail.

🌐 Interface simples e responsiva (HTML + Bootstrap).

🔄 Integração com a API Gemini para análise de linguagem natural.

🛠️ Tecnologias Utilizadas
Backend

Python 3

Flask
 → framework web para APIs e rotas

Requests
 → comunicação com a API Gemini

PyPDF2
 → leitura e extração de texto de arquivos PDF

Frontend

HTML5

Bootstrap 5
 → design responsivo

JavaScript (fetch API)

IA

Google Gemini API
 → processamento e geração de texto inteligente

Deploy

Render
 → hospedagem online gratuita

Estrutura do projeto

app.py
templates/
static/
requirements.txt
examples/
.env.example
README.md


---

## ⚙️ Como rodar localmente

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/projeto_autou.git
cd projeto_autou

#crie e ative um ambiente virtual

python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac

Instale as Dependencias
pip install -r requirements.txt

Agora, crie um arquivo .env na raiz do projeto
GEMINI_API_KEY=coloque_a_chave_aqui

Rode a aplicação
python app.py

Acesse
Acesse em: http://127.0.0.1:5000

A APLICAÇÃO TAMBÉM ESTÁ DISPONIVEL EM
https://autou-mail.onrender.com











