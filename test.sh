#!/usr/bin/env bash
set -e

echo "--- 1. INICIALIZAÇÃO DO AMBIENTE (Build e Up) ---"
docker-compose up -d --build

echo "Verificando o status dos containers:"
docker-compose ps
sleep 5

echo ""
echo "--- 2. TESTE DE ENVIO E REPLICAÇÃO ---"

echo "Enviando MENSAGEM 1 para http://localhost:5001/send"
curl -s -X POST -H "Content-Type: application/json" -d '{"message":"Ola do App1 - Mensagem Original"}' http://localhost:5001/send | jq .

echo ""
echo "Enviando MENSAGEM 2 para http://localhost:5002/send"
curl -s -X POST -H "Content-Type: application/json" -d '{"message":"Alo do App2 - Segunda Original"}' http://localhost:5002/send | jq .

sleep 3

echo ""
echo "--- 3. AVALIAÇÃO DA REPLICAÇÃO (GET /messages) ---"

echo "--> Mensagens no app1 (Porta 5001): Esperado: 2 (1 original + 1 réplica)"
curl -s http://localhost:5001/messages | jq '."total_messages", ."messages"[].message'

echo "--> Mensagens no app2 (Porta 5002): Esperado: 2 (1 original + 1 réplica)"
curl -s http://localhost:5002/messages | jq '."total_messages", ."messages"[].message'

echo "--> Mensagens no app3 (Porta 5003): Esperado: 2 (2 réplicas)"
curl -s http://localhost:5003/messages | jq '."total_messages", ."messages"[].message'

echo ""
echo "--- 4. AVALIAÇÃO DOS ARQUIVOS NO VOLUME COMPARTILHADO ---"

echo "Listando arquivos no diretório /messages_volume (volume compartilhado):"
docker exec app1_container ls -l /messages_volume

echo ""
echo "Conteúdo do LOG de app1 (Verificando se salvou M1 e replicou/recebeu M2):"
docker exec app1_container cat /messages_volume/app1_log.txt

echo ""
echo "--- FIM DOS TESTES ---"
echo "Para encerrar o ambiente: docker-compose down"
