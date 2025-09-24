# Sistema de Mensageria Distribuída (Flask + Docker Compose)

Este projeto implementa um sistema de mensagens distribuído em **Python (Flask)**, onde 3 containers (app1, app2, app3) podem enviar e replicar mensagens entre si. 
As mensagens são armazenadas em arquivos JSON dentro de um volume compartilhado, e cada serviço mantém também seu arquivo de log.

## Estrutura do Projeto
```
/avaliacao/
├── app/
│   ├── app.py              # Código principal Flask
│   ├── Dockerfile          # Dockerfile da aplicação
│   └── requirements.txt    # Dependências
├── docker-compose.yml      # Configuração do ambiente distribuído
├── test.sh                 # Script de teste automatizado
└── README.md               # Este arquivo
```

## Como Executar

### 1. Subir o ambiente
```bash
docker-compose up -d --build
```

### 2. Enviar mensagens
```bash
curl -X POST -H "Content-Type: application/json" -d '{"message":"Olá do App1"}' http://localhost:5001/send

curl -X POST -H "Content-Type: application/json" -d '{"message":"Alo do App2"}' http://localhost:5002/send
```

### 3. Consultar mensagens
```bash
curl http://localhost:5001/messages
curl http://localhost:5002/messages
curl http://localhost:5003/messages
```

### 4. Testes automatizados
```bash
chmod +x test.sh
./test.sh
```

### 5. Verificar arquivos no volume
```bash
docker exec app1 ls /messages_volume
docker exec app1 cat /messages_volume/app1_messages.json
docker exec app1 cat /messages_volume/app1_log.txt
```

### 6. Encerrar o ambiente
```bash
docker-compose down
```

## Observações Técnicas
- Cada container mantém seu próprio arquivo JSON (`<service>_messages.json`) e log (`<service>_log.txt`) no volume compartilhado.
- A replicação ocorre apenas quando a mensagem é original (não replicada).
- Logs de replicação são gravados no arquivo de log do container.

## Tecnologias
- Python 3.9
- Flask (API REST)
- Requests (comunicação entre containers)
- Docker Compose (orquestração dos serviços)

## Autores
Projeto desenvolvido para fins acadêmicos na disciplina **Computação em Nuvem (G1 - 2025/2)**.
