import asyncio
import asyncssh
import datetime
from core.ai_engine import IllusionistAI
from core.aws_queue import AttackLogger

# Inicializamos os nossos motores de IA e Mensageria
ai_engine = IllusionistAI()
logger = AttackLogger()


class HoneypotSSHServer(asyncssh.SSHServer):

    def connection_made(self, conn):
        self._client_ip = conn.get_extra_info('peername')[0]
        print(f"[+] Nova conexão recebida do IP: {self._client_ip}")

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        print(f"[*] Credenciais Capturadas -> User: {username} | Pass: {password}")

        payload = {
            "type": "credentials_capture",
            "ip": self._client_ip,
            "username": username,
            "password": password,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        asyncio.create_task(logger.send_to_sqs(payload))

        return True  # Acesso sempre concedido!


async def handle_client(process):
    process.stdout.write("Welcome to Ubuntu 22.04.4 LTS (GNU/Linux 5.15.0-101-generic x86_64)\n\n")
    process.stdout.write("root@server:~# ")

    try:
        async for command in process.stdin:
            # asyncio.create_task(logger.send_to_sqs({...}))
            cmd = command.strip()

            if not cmd:
                process.stdout.write("root@server:~# ")
                continue

            if cmd in ['exit', 'quit', 'logout']:
                process.stdout.write("logout\n")
                process.exit(0)
                break

            client_ip = process.channel.get_connection().get_extra_info('peername')[0]

            asyncio.create_task(logger.send_to_sqs({
                "type": "command_execution",
                "ip": client_ip,
                "command": cmd,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }))

            fake_output = await ai_engine.generate_fake_response(cmd)

            process.stdout.write(fake_output)
            if not fake_output.endswith('\n'):
                process.stdout.write('\n')

            process.stdout.write("root@server:~# ")

    except asyncssh.BreakReceived:
        pass


async def start_server():

    server_key = asyncssh.generate_private_key('ssh-rsa')

    await asyncssh.create_server(
        HoneypotSSHServer,
        '', 2222,
        server_host_keys=[server_key],
        process_factory=handle_client
    )
    print("[*] House Of Echoes -> SSH Honeypot ativo na porta 2222...")

    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(start_server())