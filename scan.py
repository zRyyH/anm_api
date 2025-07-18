import pdfplumber
import re
from io import BytesIO


def extrair_info_boleto_buffer(pdf_buffer: BytesIO):
    pdf_buffer.seek(0)

    with pdfplumber.open(pdf_buffer) as pdf:
        linhas = []
        for pagina in pdf.pages:
            if texto := pagina.extract_text():
                linhas.extend(texto.splitlines())

    # Buscar linha digitável
    linha_digitavel = None
    for linha in linhas:
        if m := re.search(r"(\d{5}\.\d{5} \d{5}\.\d{6} \d{5}\.\d{6} \d \d{14})", linha):
            linha_digitavel = m.group(1)
            break

    if not linha_digitavel:
        raise ValueError("Linha digitável não encontrada")

    # Extrair nosso número
    raw = re.sub(r"\D", "", linha_digitavel)
    barcode = raw[0:4] + raw[32:47] + raw[4:9] + raw[10:20] + raw[21:31]
    nosso_numero = barcode[19:][6:23]

    # Buscar sacado
    sacado = "Não encontrado"
    for i, l in enumerate(linhas):
        if l.strip().lower() == "sacado" and i + 1 < len(linhas):
            sacado = linhas[i + 1].strip().rstrip(".").split("CPF/CNPJ")[0].strip()
            break

    return {
        "codigo_de_barras": linha_digitavel,
        "nosso_numero": nosso_numero,
        "sacado": sacado,
    }
