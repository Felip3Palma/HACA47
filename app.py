from flask import Flask, jsonify
import json
import subprocess

app = Flask(__name__)

# Carrega as perguntas do arquivo JSON
with open('simples.json', 'r', encoding='utf-8') as file:
    perguntas = json.load(file)


# Função para interagir com o Ollama
def perguntar_ollama(pergunta):
    """ Envia uma pergunta ao Ollama e retorna a resposta.
     Parâmetros: pergunta (str): A pergunta a ser enviada ao Ollama.
    Retorna: str: A resposta do Ollama ou uma mensagem de erro. """

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2"],
            input=pergunta,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'  # Define a codificação da saída
        )
        print(f"Resposta do Ollama: {result.stdout}")  # Adicione esse print para debug
        if result.stdout:  # Verifica se stdout não é None
            return result.stdout.strip()  # Retorna a resposta do Ollama
        else:
            return "Nenhuma resposta obtida do Ollama."
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar Ollama: {e.stderr.strip()}"



# Rota para a página inicial
@app.route('/')
def index():
    """ Rota para a página inicial, que avalia as respostas geradas pelo Ollama e exibe os resultados em formato HTML.
    Retorna: str: HTML contendo as perguntas e respostas geradas pela IA, bem como se as respostas estão corretas. """

    resultados = []

    for idx, pergunta in enumerate(perguntas):
        questao = pergunta["pergunta"]
        resposta_correta = pergunta["resposta"]

        # Envia a pergunta ao Ollama e captura a resposta
        resposta_ia = perguntar_ollama(questao)

        # Compara a resposta do Ollama com a resposta correta
        correta = resposta_ia.lower() == resposta_correta.lower()

        resultados.append({
            "id": idx,
            "pergunta": questao,
            "resposta_ia": resposta_ia,
            "resposta_correta": resposta_correta,
            "correta": correta
        })

    # Gera uma resposta HTML simples para exibir as perguntas e respostas
    html = "<h1>Resultados</h1><ul>"
    for resultado in resultados:
        html += f"<li><strong>Pergunta:</strong> {resultado['pergunta']}<br>"
        html += f"<strong>Resposta IA:</strong> {resultado['resposta_ia']}<br>"
        html += f"<strong>Resposta Correta:</strong> {resultado['resposta_correta']}<br>"
        html += f"<strong>Correta:</strong> {'Sim' if resultado['correta'] else 'Não'}</li><br>"
    html += "</ul>"

    return html


@app.route('/avaliar', methods=['GET'])
def avaliar_respostas():
    """ Endpoint para avaliar as respostas geradas pelo Ollama.
     Retorna: json: Uma lista de resultados contendo a pergunta, a resposta gerada pela IA, a resposta correta
     e verifica se a resposta está correta. """

    resultados = []

    for idx, pergunta in enumerate(perguntas):
        questao = pergunta["pergunta"]
        resposta_correta = pergunta["resposta"]

        # Envia a pergunta ao Ollama e captura a resposta
        resposta_ia = perguntar_ollama(questao)

        # Compara a resposta do Ollama com a resposta correta
        correta = resposta_ia.lower() == resposta_correta.lower()

        resultados.append({
            "id": idx,
            "pergunta": questao,
            "resposta_ia": resposta_ia,
            "resposta_correta": resposta_correta,
            "correta": correta
        })

    return jsonify(resultados)


if __name__ == '__main__':
    app.run(debug=True)
