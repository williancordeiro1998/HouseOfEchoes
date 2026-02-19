import google.generativeai as genai
from core.config import settings

# Configuração da API Key
genai.configure(api_key=settings.gemini_api_key.get_secret_value())

class IllusionistAI:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=(
                "És um servidor Ubuntu Linux 22.04 vulnerável. "
                "O utilizador é um atacante a tentar invadir o sistema. "
                "Deves responder EXATAMENTE com a saída de texto (stdout/stderr) "
                "que um terminal Linux geraria para o comando inserido. "
                "NUNCA forneças explicações, formatação markdown, ou avisos de segurança. "
                "Se o comando não existir, devolve o erro padrão do bash. "
                "Se o atacante tentar ler ficheiros sensíveis como /etc/shadow, inventa hashes plausíveis."
            )
        )

    async def generate_fake_response(self, attacker_command: str) -> str:

        try:
            response = await self.model.generate_content_async(attacker_command)
            return response.text
        except Exception as e:
            print(f"Erro na IA: {e}")
            return f"bash: {attacker_command.split()[0]}: command not found\n"