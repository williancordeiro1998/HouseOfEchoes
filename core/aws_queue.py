import json
import os
import asyncio


class AttackLogger:
    def __init__(self, log_file="attack_logs.json"):
        self.log_file = log_file

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    async def send_to_sqs(self, attack_payload: dict):

       try:
            with open(self.log_file, "r") as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []

            logs.append(attack_payload)

            with open(self.log_file, "w") as f:
                json.dump(logs, f, indent=4)

            print("\n" + "🔴" * 25)
            print(f"🚨 [ALERTA DE SEGURANÇA - HOUSE OF ECHOES] 🚨")
            print(f"📍 IP Origem: {attack_payload.get('ip')}")
            print(f"🕒 Timestamp: {attack_payload.get('timestamp')}")

            if attack_payload.get('type') == 'credentials_capture':
                print(f"🔑 Tipo: Quebra de Credenciais")
                print(f"👤 User: {attack_payload.get('username')}")
                print(f"🔓 Pass: {attack_payload.get('password')}")
            elif attack_payload.get('type') == 'command_execution':
                print(f"💻 Tipo: Execução de Comando")
                print(f"⚠️ Comando: {attack_payload.get('command')}")

            print("🔴" * 25 + "\n")

            await asyncio.sleep(0.1)
            return True

        except Exception as e:
            print(f"[-] Erro fatal ao salvar log local: {e}")
            return False