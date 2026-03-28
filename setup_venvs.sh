#!/bin/bash

SERVICES=("product-service" "user-service" "order-service" "inventory-service" "payment-service")

for service in "${SERVICES[@]}"; do
    echo "🔧 Configurando $service..."
    cd "$service"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ..
done

echo "✅ Todos os ambientes virtuais foram criados com sucesso!"