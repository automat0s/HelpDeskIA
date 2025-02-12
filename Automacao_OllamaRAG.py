import os
import json
import csv
from dotenv import load_dotenv
from ragflow_sdk import RAGFlow

# Carrega as variáveis do arquivo .env
load_dotenv()

API_KEY = os.getenv("RAGFLOW_API_KEY")
BASE_URL = os.getenv("RAGFLOW_BASE_URL")

if not API_KEY or not BASE_URL:
    raise ValueError("API_KEY ou BASE_URL não definidas no .env")

# Inicializa o RAGFlow
rag_object = RAGFlow(api_key=API_KEY, base_url=BASE_URL)

# Lista os assistentes disponíveis
assistants = rag_object.list_chats()

# Identifica os assistentes pelo nome
jarvis_assistant = next((a for a in assistants if a.name == "Jarvis"), None)
siri_assistant = next((a for a in assistants if a.name == "Siri"), None)

if not jarvis_assistant or not siri_assistant:
    raise ValueError("Assistente 'Jarvis' ou 'Siri' não encontrado.")

# Criar sessões para cada assistente
jarvis_session = jarvis_assistant.create_session()
siri_session = siri_assistant.create_session()

# Ler perguntas do dataset.json
with open("dataset.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    faqs = data.get("faq", [])

# Listas para armazenar as respostas dos assistentes
respostas_jarvis = []
respostas_siri = []

# Faz perguntas para cada assistente e armazena as respostas
for item in faqs:
    pergunta = item["question"]
    resposta_esperada = item["answer"]

    print(f"\nPergunta: {pergunta}")

    try:
        # Obtendo resposta do Jarvis
        jarvis_resposta = "".join(ans.content for ans in jarvis_session.ask(pergunta, stream=True))
    except Exception as e:
        jarvis_resposta = f"Erro: {e}"

    try:
        # Obtendo resposta da Siri
        siri_resposta = "".join(ans.content for ans in siri_session.ask(pergunta, stream=True))
    except Exception as e:
        siri_resposta = f"Erro: {e}"

    # Adiciona as respostas nas listas correspondentes
    respostas_jarvis.append([pergunta, resposta_esperada, jarvis_resposta])
    respostas_siri.append([pergunta, resposta_esperada, siri_resposta])

# Salva as respostas do Jarvis em um CSV
with open("respostasJarvis.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Pergunta", "Resposta Esperada", "Resposta Jarvis"])
    writer.writerows(respostas_jarvis)

# Salva as respostas da Siri em um CSV
with open("respostasSiri.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Pergunta", "Resposta Esperada", "Resposta Siri"])
    writer.writerows(respostas_siri)

print("\nRespostas salvas em 'respostasJarvis.csv' e 'respostasSiri.csv' com sucesso! ✅")
