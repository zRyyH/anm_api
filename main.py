from utils import gerar_csv_em_buffer, zipar_arquivos_em_buffer
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, FastAPI
from models import EmailMessageData
from scraping import get_invoices
from cachetools import TTLCache
from config import EMAIL_CONFIG
from mailer import EmailSender
from directus import get_me
import logging
import locale
import uuid

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
logger = logging.getLogger(__name__)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
temp_buffers = TTLCache(maxsize=1000, ttl=900)  # 15 minutos


def check_auth(token: str = Depends(oauth2_scheme)):
    user = get_me(token)
    if user.get("status") != "active":
        raise HTTPException(status_code=401, detail="Não autorizado!")
    return user


@app.get("/consult")
def consult(cpfcnpj: str, _=Depends(check_auth)):
    try:
        request_token = str(uuid.uuid4())
        dados, buffers = get_invoices(cpfcnpj)
        temp_buffers[request_token] = {"buffers": buffers, "data": dados}
        return {"request_token": request_token, "data": dados}
    except Exception as e:
        logger.error(f"Erro na consulta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/send_email")
def send_email(request_token: str, email: str, _=Depends(check_auth)):
    try:
        entry = temp_buffers.get(request_token)
        if not entry:
            return {"error": "Token inválido ou expirado"}

        dados = entry["data"]

        # Gerar resumo
        body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; color: #333; margin: 0; padding: 20px; background: #fafafa;">
            <div style="max-width: 480px; margin: auto; background: #fff; border: 1px solid #e0e0e0; border-radius: 4px; padding: 16px;">
            <h2 style="font-size: 18px; margin: 0 0 12px;">Resumo de Faturas</h2>
            <p style="margin: 4px 0;"><strong>Empresa:</strong> {dados[0]["sacado"]}</p>
            <p style="margin: 4px 0;"><strong>Total de faturas:</strong> {len(dados)}</p>
            <p style="margin: 4px 0;"><strong>Valor total:</strong> {locale.currency(sum(item["valor"] for item in dados), symbol=True, grouping=True)}</p>
            <p style="margin: 4px 0;"><strong>Valor total atualizado:</strong> {locale.currency(sum(item["valorAtualizado"] for item in dados), symbol=True, grouping=True)}</p>
            </div>
        </body>
        </html>
        """

        email_data = EmailMessageData(
            subject="Arquivos múltiplos",
            body=body,
            from_addr=EMAIL_CONFIG["username"],
            to_addrs=[email],
            html=True,
        )

        EmailSender().send(
            email_data,
            [
                {"filename": "planilha.csv", "buffer": gerar_csv_em_buffer(dados)},
                {
                    "filename": "boletos_grus.zip",
                    "buffer": zipar_arquivos_em_buffer(entry["buffers"]),
                },
            ],
        )

        return {"status": "sucesso", "message": "E-mail enviado"}
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
