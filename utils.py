from io import BytesIO
import pandas as pd
import requests
import zipfile
import logging
import time

logger = logging.getLogger(__name__)


def solve_recaptcha_v2(site_url, site_key, api_key):
    url = "https://api.capsolver.com"

    # Criar task
    r = requests.post(
        f"{url}/createTask",
        json={
            "clientKey": api_key,
            "task": {
                "type": "ReCaptchaV2Task",
                "websiteURL": site_url,
                "websiteKey": site_key,
            },
        },
    ).json()

    task_id = r.get("taskId")
    if not task_id:
        raise Exception(f"Falha ao criar task: {r}")

    # Aguardar solução
    for _ in range(30):
        time.sleep(2)
        check = requests.post(
            f"{url}/getTaskResult", json={"clientKey": api_key, "taskId": task_id}
        ).json()

        if check["status"] == "ready":
            return check["solution"]["gRecaptchaResponse"]

    raise Exception(f"Falha ao resolver captcha: {check}")


def gerar_csv_em_buffer(dados: list) -> BytesIO:
    buffer = BytesIO()
    pd.DataFrame(dados).to_csv(buffer, index=False, encoding="utf-8-sig")
    buffer.seek(0)
    return buffer


def zipar_arquivos_em_buffer(arquivos: list) -> BytesIO:
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for arq in arquivos:
            arq["buffer"].seek(0)
            zipf.writestr(arq["filename"], arq["buffer"].read())
    zip_buffer.seek(0)
    return zip_buffer
