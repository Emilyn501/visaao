import os
from flask import Flask, request, render_template, redirect, url_for
from google.genai import client

# Inicializa o Flask
app = Flask(__name__)

API_KEY = "AIzaSyBbWk0lwWrWA-h2flHchSjSoLfM-CKbwCo"
# Modelo a ser usado
MODEL_NAME = 'gemini-2.5-flash'

try:
    # Instanciação correta do cliente
    genai_client = client.Client(api_key=API_KEY)
except Exception as e:
    # Tratamento de erro na configuração
    print(f"Erro ao configurar a API: {e}")
    genai_client = None

# Variável global para armazenar o histórico de conversas
chat_history = [] 

# Função para gerar a resposta do chatbot (Corrigida)
def get_vision_response(prompt):
    """Gera a resposta do modelo com um prompt de sistema e usa o client correto."""
    if not genai_client:
        return "Erro: Cliente de IA não configurado. Verifique sua chave API e o setup."
        
    system_instruction = (
        "Você é um assistente informativo sobre problemas e condições de visão (Oftalmologia). "
        "Suas respostas devem ser claras, concisas e sempre incluir um aviso de que "
        "você não é um médico e que a pessoa deve consultar um oftalmologista para diagnóstico e tratamento. "
        "Responda à seguinte pergunta do usuário de forma útil e cautelosa."
    )
    
    try:
        # Uso correto do generate_content (sem o erro models.get)
        response = genai_client.models.generate_content(
            model=MODEL_NAME, # O nome do modelo é passado aqui
            contents=prompt,
            config={"system_instruction": system_instruction}
        )
        return response.text
    # Bloco 'except' inserido para corrigir o SyntaxError
    except Exception as e:
        print(f"Erro ao chamar a API: {e}")
        return ("Desculpe, ocorreu um erro ao tentar gerar a resposta da IA. "
                "Detalhes do erro: Consulte o log do servidor para mais informações.")


# --- Rota Principal para Exibir e Processar o Chat ---

@app.route('/', methods=['GET', 'POST'])
def chat_interface():
    global chat_history
    
    if not chat_history:
        # Mensagem inicial apenas na primeira carga
        initial_message = {
            'sender': 'ai',
            'text': ("Olá! Eu sou o VisioAssist. Posso te ajudar com informações gerais sobre "
                     "problemas de visão. **Lembre-se: consulte sempre um oftalmologista.** "
                     "Como posso te ajudar?")
        }
        chat_history.append(initial_message)
    
    if request.method == 'POST':
        user_message = request.form.get('user_input', '').strip()
        
        if user_message:
            chat_history.append({'sender': 'user', 'text': user_message})
            ai_response = get_vision_response(user_message)
            chat_history.append({'sender': 'ai', 'text': ai_response})
            
            # Redireciona para o GET para recarregar a página com o histórico
            return redirect(url_for('chat_interface'))

    # Renderiza o template HTML, passando o histórico
    return render_template('index.html', chat_history=chat_history)

if __name__ == '__main__':
    # Inicializa o servidor Flask
    app.run(debug=True, port=5000)