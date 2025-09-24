from flask import Flask, request, jsonify
import json
import os
import requests
import logging
from datetime import datetime

# --- Configurações ---
app = Flask(__name__)
VOLUME_PATH = '/messages_volume'
MESSAGES_DIR = os.path.join(VOLUME_PATH, 'data')
HOST_NAME = os.environ.get('SERVICE_NAME', 'unknown_service')
MESSAGES_FILE = os.path.join(MESSAGES_DIR, f'{HOST_NAME}_messages.json')

OTHER_SERVICES = os.environ.get('OTHER_SERVICES', '').split(',') 
OTHER_SERVICES = [s for s in OTHER_SERVICES if s] 

LOG_FILE = os.path.join(VOLUME_PATH, f'{HOST_NAME}_log.txt')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

os.makedirs(MESSAGES_DIR, exist_ok=True)


def load_messages():
    """Carrega as mensagens do arquivo JSON específico do serviço."""
    if not os.path.exists(MESSAGES_FILE):
        return []
    try:
        with open(MESSAGES_FILE, 'r') as f:
            content = f.read()
            return json.loads(content) if content else []
    except Exception as e:
        logger.error(f"Erro ao carregar mensagens: {e}")
        return []

def save_message(message_data):
    """Salva uma nova mensagem no arquivo JSON local."""
    messages = load_messages()
    message_data['source_service'] = message_data.get('source_service', HOST_NAME)
    message_data['received_by'] = HOST_NAME
    message_data['timestamp'] = datetime.now().isoformat()
    messages.append(message_data)
    
    try:
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=4)
        logger.info(f"Mensagem salva localmente: {message_data['message']}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem: {e}")
        return False

def replicate_message(message_data):
    """Envia a mensagem para os outros containers via POST /send."""
    
    if 'source_service' not in message_data:
        message_data['source_service'] = HOST_NAME

    if message_data.get('source_service') != HOST_NAME:
        return

    if 'received_by' in message_data:
        del message_data['received_by']
    
    for service_name in OTHER_SERVICES:
        url = f'http://{service_name}:5000/send' 
        try:
            response = requests.post(url, json=message_data, timeout=2) 
            if response.status_code == 200:
                logger.info(f"Mensagem replicada com sucesso para {service_name}.")
            else:
                logger.warning(f"Falha na replicação para {service_name}. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de comunicação ao replicar para {service_name}: {e}")

# --- Endpoints ---

@app.route('/send', methods=['POST'])
def send_message():
    """Endpoint para receber a mensagem, salvar e replicar."""
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"status": "error", "message": "JSON inválido."}), 400

    if not data or 'message' not in data:
        return jsonify({"status": "error", "message": "Campo 'message' é obrigatório."}), 400

    save_message(data)

    if request.remote_addr != '127.0.0.1' and data.get('source_service') is None:
        replicate_message(data)
    elif data.get('source_service') == HOST_NAME and request.remote_addr == '127.0.0.1':
        replicate_message(data)

    return jsonify({"status": "success", "message": f"Mensagem recebida e processada por {HOST_NAME}."}), 200

@app.route('/messages', methods=['GET'])
def get_messages():
    """Endpoint para retornar todas as mensagens armazenadas localmente."""
    messages = load_messages()
    return jsonify({
        "service": HOST_NAME,
        "total_messages": len(messages),
        "messages": messages
    }), 200

if __name__ == '__main__':
    logger.info(f"Serviço {HOST_NAME} iniciado e rodando na porta 5000 interna.")
    app.run(host='0.0.0.0', port=5000)
