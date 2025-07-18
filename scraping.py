from concurrent.futures import ThreadPoolExecutor, as_completed
from scan import extrair_info_boleto_buffer
from utils import solve_recaptcha_v2
from datetime import datetime
from config import SETTINGS
from io import BytesIO
import requests
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "accept": "*/*",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "authorization": "Bearer undefined",
    "content-type": "application/json",
    "origin": "https://app.anm.gov.br",
    "referer": "https://app.anm.gov.br/sinarc-site/anonimo/pagar-anonimo",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0.0.0",
}


def extract_bill(idCredito, cpfcnpjTitular, token):
    r = requests.post(
        "https://app.anm.gov.br/sinarc-api/v1/Boleto/ObterAnonimo",
        headers=HEADERS,
        json={
            "idCredito": idCredito,
            "cpfcnpjTitular": cpfcnpjTitular,
            "credencial": token,
        },
    )
    return r.content


def extract_invoice(cpfCnpj, token):
    headers = HEADERS.copy()
    headers["content-type"] = "application/x-www-form-urlencoded;charset=UTF-8"

    payload = {
        "cpfCnpj": cpfCnpj,
        "credencial": token,
        "paginaAtual": "1",
        "itensPorPagina": "1000000",
        "decrescente": "true",
        "sucesso": "true",
    }

    r = requests.post(
        "https://app.anm.gov.br/sinarc-api/v1/Receita/ObterCreditosAnonimo",
        headers=headers,
        data=payload,
    )
    return r.json()


def process_invoice(fatura, token):
    buffer_pdf = BytesIO(extract_bill(fatura["id"], fatura["cpfcnpj"], token))
    info = extrair_info_boleto_buffer(buffer_pdf)

    proc = f"{str(fatura['numeroProcessoMinerario'])[:3]}.{str(fatura['numeroProcessoMinerario'])[3:]}"
    data_venc = datetime.fromisoformat(fatura["vencimento"]).strftime("%Y_%m")

    return {
        "descricaoOrigemReceita": fatura["descricaoOrigemReceita"],
        "numeroProcessoMinerario": f"{fatura['numeroProcessoMinerario']}/{fatura['anoProcessoMinerario']}",
        "sacado": info["sacado"],
        "valor": fatura["valor"],
        "valorAtualizado": fatura["valorAtualizado"],
        "vencimento": fatura["vencimento"],
        "numeroReferencia": info["nosso_numero"],
        "codigoBarra": info["codigo_de_barras"],
    }, {
        "buffer": buffer_pdf,
        "filename": f"{proc}_{fatura['anoProcessoMinerario']}-264-RES-TAH-{data_venc}-BOLETO.pdf",
    }


def get_invoices(cnpjCpf):
    token = solve_recaptcha_v2(
        SETTINGS["site_url"], SETTINGS["site_key"], SETTINGS["api_key"]
    )

    faturas = extract_invoice(cnpjCpf, token)["valor"]["resultado"]
    invoices, buffers = [], []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_invoice, f, token) for f in faturas]
        for future in as_completed(futures):
            invoice, buffer = future.result()
            invoices.append(invoice)
            buffers.append(buffer)

    logger.info(f"Processadas {len(invoices)} faturas")
    return invoices, buffers
