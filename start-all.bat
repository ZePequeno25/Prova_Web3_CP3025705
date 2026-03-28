@echo off
chcp 65001 >nul
echo ========================================================
echo     INICIANDO TODOS OS MICROSSERVIÇOS - WINDOWS
echo ========================================================
echo.

echo Iniciando Catálogo Service...
start cmd /k "cd catalogo-service && echo ====================================== && echo Catálogo Service - Porta 8001 && echo ====================================== && pip install -r requirements.txt && uvicorn main:app --reload --port 8001"

echo Iniciando Usuários Service...
start cmd /k "cd usuarios-service && echo ====================================== && echo Usuários Service - Porta 8002 && echo ====================================== && pip install -r requirements.txt && uvicorn main:app --reload --port 8002"

echo Iniciando Pedidos Service...
start cmd /k "cd pedidos-service && echo ====================================== && echo Pedidos Service - Porta 8003 && echo ====================================== && pip install -r requirements.txt && uvicorn main:app --reload --port 8003"

echo Iniciando Estoque Service...
start cmd /k "cd estoque-service && echo ====================================== && echo Estoque Service - Porta 8004 && echo ====================================== && pip install -r requirements.txt && uvicorn main:app --reload --port 8004"

echo Iniciando Pagamento Service...
start cmd /k "cd pagamento-service && echo ====================================== && echo Pagamento Service - Porta 8005 && echo ====================================== && pip install -r requirements.txt && uvicorn main:app --reload --port 8005"

echo.
echo ========================================================
echo Todos os serviços foram iniciados em janelas CMD separadas!
echo Aguarde alguns segundos até todos carregarem.
echo Para parar um serviço, pressione Ctrl + C na janela correspondente.
echo ========================================================

pause