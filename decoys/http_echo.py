import datetime
import asyncio
from fastapi import FastAPI, Request
from core.aws_queue import AttackLogger

app = FastAPI(docs_url=None, redoc_url=None)  # Escondemos a documentação real
logger = AttackLogger()


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all_routes(request: Request, path: str):
    """
    Captura qualquer tentativa de acesso web e regista o ataque.
    """
    client_ip = request.client.host
    method = request.method
    headers = dict(request.headers)

    # Tentamos ler o corpo da requisição (ex: tentativas de SQL Injection num POST)
    try:
        body = await request.body()
        body_str = body.decode('utf-8')
    except:
        body_str = ""

    payload = {
        "type": "web_attack",
        "ip": client_ip,
        "method": method,
        "path": f"/{path}",
        "headers": headers,
        "body": body_str,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    # Envia para a AWS em background sem atrasar a resposta ao atacante
    asyncio.create_task(logger.send_to_sqs(payload))
    print(f"[!] Ataque Web detectado de {client_ip} no endpoint /{path}")

    # Mentimos para o atacante simulando um erro de servidor vulnerável
    return {"error": "Database connection failed", "code": 500, "debug": "Check config.php"}

# Para rodar: uvicorn decoys.http_echo:app --port 8080