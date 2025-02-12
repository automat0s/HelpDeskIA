import csv
import subprocess
from sentence_transformers import SentenceTransformer, util

# Inicializa o modelo de embeddings
modelo_embeddings = SentenceTransformer('all-MiniLM-L6-v2')

# Função para carregar perguntas do arquivo CSV
def carregar_perguntas(arquivo_csv):
    """
    Carrega as perguntas e respostas esperadas de um arquivo CSV.
    
    :param arquivo_csv: Caminho para o arquivo CSV.
    :return: Lista de perguntas com respostas esperadas.
    """
    perguntas_respostas = []
    try:
        with open(arquivo_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                perguntas_respostas.append({
                    'question': row['question'],
                    'expected_answer': row['answer']
                })
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
    return perguntas_respostas

# Função para enviar perguntas ao Ollama via terminal
def enviar_para_ollama_terminal(pergunta, modelo):
    """
    Envia uma pergunta para o Ollama via terminal e retorna a resposta.
    
    :param pergunta: Pergunta a ser enviada.
    :param modelo: Modelo a ser utilizado.
    :return: Resposta do Ollama.
    """
    try:
        # Comando para executar o Ollama
        command = ["ollama", "run", modelo, pergunta]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()  # Retorna a saída do comando
        else:
            return f"Erro ao executar o comando: {result.stderr.strip()}"
    except Exception as e:
        return f"Erro ao conectar com o Ollama: {e}"

# Função para calcular a similaridade semântica
def calcular_similaridade_semantica(resposta_modelo, resposta_esperada):
    """
    Calcula a similaridade semântica entre duas respostas usando Sentence Transformers.
    
    :param resposta_modelo: Resposta gerada pelo modelo.
    :param resposta_esperada: Resposta esperada no dataset.
    :return: Score de similaridade semântica (0 a 1).
    """
    embeddings_modelo = modelo_embeddings.encode(resposta_modelo, convert_to_tensor=True)
    embeddings_esperada = modelo_embeddings.encode(resposta_esperada, convert_to_tensor=True)
    similaridade = util.pytorch_cos_sim(embeddings_modelo, embeddings_esperada)
    return similaridade.item()

# Função principal para processar perguntas
def processar_perguntas(arquivo_csv, arquivo_saida, modelo):
    """
    Processa perguntas, compara respostas e salva os resultados em outro arquivo CSV.
    
    :param arquivo_csv: Caminho do arquivo CSV de entrada.
    :param arquivo_saida: Caminho do arquivo CSV para salvar os resultados.
    :param modelo: Modelo a ser utilizado.
    """
    perguntas_respostas = carregar_perguntas(arquivo_csv)
    if not perguntas_respostas:
        print("Nenhuma pergunta encontrada.")
        return

    resultados = []
    total_similaridade = 0
    for item in perguntas_respostas:
        pergunta = item['question']
        resposta_esperada = item['expected_answer']
        print(f"Perguntando: {pergunta}")
        
        resposta_modelo = enviar_para_ollama_terminal(pergunta, modelo)
        similaridade = calcular_similaridade_semantica(resposta_modelo, resposta_esperada)
        total_similaridade += similaridade

        print(f"Resposta Esperada: {resposta_esperada}")
        print(f"Resposta Modelo: {resposta_modelo}")
        print(f"Similaridade Semântica: {similaridade:.2f}\n")

        resultados.append({
            'question': pergunta,
            'expected_answer': resposta_esperada,
            'model_answer': resposta_modelo,
            'similarity_score': f"{similaridade:.2f}"
        })

    # Calcula a taxa de acerto em porcentagem
    taxa_acerto = (total_similaridade / len(perguntas_respostas)) * 100
    print(f"Taxa de Acerto ({modelo}): {taxa_acerto:.2f}%")

    # Salva os resultados em um novo arquivo CSV
    try:
        with open(arquivo_saida, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['question', 'expected_answer', 'model_answer', 'similarity_score'])
            writer.writeheader()
            writer.writerows(resultados)
        print(f"Resultados salvos em: {arquivo_saida}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo CSV: {e}")

# Uso do script
if __name__ == "__main__":
    arquivo_entrada = "/home/marcola/Documentos/Desenvolvimento/Python/HelpDeskIA/dataset.csv"  # Substitua pelo caminho do seu arquivo CSV de entrada
    processar_perguntas(arquivo_entrada, "resultados_llama3.1.csv", "llama3.1")
    processar_perguntas(arquivo_entrada, "resultados_qwen2.5.csv", "qwen2.5")
