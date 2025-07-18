# ANM API

API para consulta e envio de boletos do sistema ANM (Agência Nacional de Mineração).

## Instalação

1. Clone o repositório
2. Copie `.env.example` para `.env` e configure as variáveis
3. Execute com Docker:
   ```bash
   docker-compose up -d
   ```

## Endpoints

- `GET /consult?cpfcnpj={cpfcnpj}` - Consulta faturas
- `GET /send_email?request_token={token}&email={email}` - Envia faturas por email

## Autenticação

Todos os endpoints requerem token Bearer obtido via Directus.