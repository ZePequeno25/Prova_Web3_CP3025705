#!/bin/bash

echo "🚀 Iniciando os 5 microsserviços em terminais separados (Linux)..."

# Lista de serviços
SERVICES=(
  "🟢 Product Service|product-service|8001"
  "🔵 User Service|user-service|8002"
  "🟠 Order Service|order-service|8003"
  "🟣 Inventory Service|inventory-service|8004"
  "🔴 Payment Service|payment-service|8005"
)

for service in "${SERVICES[@]}"; do
  NAME=$(echo $service | cut -d'|' -f1)
  FOLDER=$(echo $service | cut -d'|' -f2)
  PORT=$(echo $service | cut -d'|' -f3)

  echo "Iniciando $NAME na porta $PORT..."

  # Abre um novo terminal com o serviço
  gnome-terminal --title="$NAME" -- bash -c "
    cd $FOLDER &&
    source venv/bin/activate &&
    echo '✅ $NAME rodando na porta $PORT' &&
    uvicorn main:app --host 0.0.0.0 --port $PORT --reload &&
    exec bash
  " &

  sleep 1.5   # pequena pausa para não abrir tudo ao mesmo tempo
done

echo ""
echo "✅ Todos os 5 serviços foram iniciados em terminais separados!"
echo "Acesse as APIs em:"
echo "• Product   → http://localhost:8001"
echo "• User      → http://localhost:8002"
echo "• Order     → http://localhost:8003"
echo "• Inventory → http://localhost:8004"
echo "• Payment   → http://localhost:8005"
echo ""
echo "Para parar todos: feche as janelas ou use Ctrl+C em cada terminal."