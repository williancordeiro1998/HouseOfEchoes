import asyncio
import json
import aiobotocore.session
from core.config import settings
from core.ai_engine import IllusionistAI

ai_engine = IllusionistAI()


async def poll_sqs():
    """Consome as mensagens da AWS SQS e classifica a ameaça com IA."""
    session = aiobotocore.session.get_session()

    print("[*] Worker iniciado. A aguardar ataques na SQS...")

    async with session.create_client(
            'sqs', region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key.get_secret_value()
    ) as client:
        while True:
            # Long polling: espera até 20 segundos por uma nova mensagem (reduz custos AWS)
            response = await client.receive_message(
                QueueUrl=settings.sqs_queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20
            )

            if 'Messages' in response:
                for msg in response['Messages']:
                    receipt_handle = msg['ReceiptHandle']
                    attack_data = json.loads(msg['Body'])

                    print(f"\n[+] Novo ataque recebido para processamento: IP {attack_data.get('ip')}")

                    # 1. Usar a IA para classificar a severidade do ataque
                    # prompt: "Analisa este log JSON. Responde apenas com um nível de ameaça: LOW, MEDIUM, ou CRITICAL."
                    severity = await ai_engine.model.generate_content_async(
                        f"Classifica esta ameaça (LOW/MEDIUM/CRITICAL): {json.dumps(attack_data)}"
                    )

                    attack_data['severity'] = severity.text.strip()
                    print(f"[*] Classificação da IA: {attack_data['severity']}")

                    # 2. Aqui salvaria no AWS DynamoDB ou noutro banco de dados
                    # await db.save(attack_data)

                    # 3. Apaga a mensagem da fila para não a processar de novo
                    await client.delete_message(
                        QueueUrl=settings.sqs_queue_url,
                        ReceiptHandle=receipt_handle
                    )
            else:
                await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(poll_sqs())