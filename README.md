# Chatbot de Reservas Pila

Este projeto implementa um chatbot para gerir reservas para o restaurante "Pila", acessível através de um widget web e do WhatsApp.

## Funcionalidades

*   Recebe pedidos de reserva via chat (web ou WhatsApp).
*   Recolhe informações necessárias: nome, telefone, email (opcional), data, hora, número de pessoas.
*   Confirma os detalhes com o utilizador.
*   Guarda as reservas confirmadas numa base de dados PostgreSQL.
*   Fornece um ID de reserva após a confirmação.
*   (Futuro) Poderá ser estendido para listar, atualizar ou cancelar reservas.

## Arquitetura

O sistema é composto por:

1.  **Backend (Flask):** Aplicação principal que gere a lógica do chat, a comunicação com a base de dados e expõe APIs.
    *   `/api/reservations/`: Endpoints para gerir reservas (criar, listar, etc.).
    *   `/api/chat/`: Endpoint para processar mensagens do widget web.
    *   `/api/whatsapp/`: Endpoint (webhook) para processar mensagens do WhatsApp (via Twilio).
2.  **Base de Dados (PostgreSQL):** Armazena as informações das reservas.
3.  **Frontend (Widget Web):** Interface HTML, CSS e JavaScript para integrar no website.
4.  **Integração WhatsApp:** Utiliza a API do WhatsApp Business (via Twilio) para comunicação.

## Estrutura do Projeto (`pila_chatbot_backend`)

```
.venv/
src/
├── models/
│   └── reservation.py    # Modelo SQLAlchemy para a tabela de reservas
├── routes/
│   ├── chat.py           # Lógica e API para o chat web
│   ├── reservation.py    # API para operações CRUD de reservas
│   └── whatsapp.py       # Lógica e API (webhook) para o chat WhatsApp
├── static/
│   ├── index.html        # HTML do widget de chat
│   ├── script.js         # JavaScript do widget de chat
│   └── style.css         # CSS do widget de chat
└── main.py             # Ponto de entrada da aplicação Flask
requirements.txt        # Dependências Python
README.md               # Este ficheiro
```

## Configuração e Execução Local

1.  **Pré-requisitos:**
    *   Python 3.11+
    *   PostgreSQL
    *   `venv` (normalmente incluído com Python)

2.  **Clonar/Copiar o Projeto:** Obtenha os ficheiros do projeto.

3.  **Configurar Base de Dados PostgreSQL:**
    *   Crie uma base de dados (ex: `pila_reservations`).
    *   Crie um utilizador e senha (ex: `pila_user` / `pila_password`).
    *   Conceda privilégios ao utilizador na base de dados.
    *   *Comandos Exemplo:*
        ```sql
        CREATE DATABASE pila_reservations;
        CREATE USER pila_user WITH PASSWORD 'pila_password';
        GRANT ALL PRIVILEGES ON DATABASE pila_reservations TO pila_user;
        ```

4.  **Configurar Ambiente Virtual e Dependências:**
    ```bash
    cd pila_chatbot_backend
    python3.11 -m venv venv
    source venv/bin/activate  # Ou venv\Scripts\activate no Windows
    pip install -r requirements.txt
    ```

5.  **Variáveis de Ambiente (Opcional):** A aplicação utiliza valores padrão para a base de dados, mas pode configurá-los através de variáveis de ambiente se necessário (ex: `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `PORT`, `FLASK_SECRET_KEY`).

6.  **Executar a Aplicação:**
    ```bash
    source venv/bin/activate
    python src/main.py
    ```
    A aplicação estará acessível em `http://localhost:5000` (ou na porta definida pela variável `PORT`).

## Integração

### Widget Web

1.  Copie os ficheiros `index.html`, `style.css`, e `script.js` da pasta `src/static/` para o seu servidor web.
2.  Adapte o `index.html` e `style.css` para incorporar o widget no design do seu website. Pode precisar de colocar o conteúdo de `index.html` dentro de uma `div` específica na sua página existente e ajustar o CSS.
3.  Certifique-se de que o JavaScript (`script.js`) é carregado na sua página.
4.  **Importante:** O `script.js` faz chamadas à API em `/api/chat/`. Se o backend estiver a correr num domínio/porta diferente do seu website, terá de:
    *   Atualizar o URL no `fetch` dentro de `script.js` para o endereço completo do backend (ex: `http://seu-backend.com/api/chat/`).
    *   Configurar CORS (Cross-Origin Resource Sharing) no backend Flask para permitir pedidos do domínio do seu website.

### WhatsApp (via Twilio)

1.  **Conta Twilio:** Necessita de uma conta Twilio com um número de telefone habilitado para WhatsApp.
2.  **Configurar Webhook:** No painel da Twilio, configure o webhook para mensagens recebidas no seu número WhatsApp para apontar para o URL público da sua aplicação Flask, seguido de `/api/whatsapp/`.
    *   *Exemplo (usando o URL temporário):* `http://5000-iu7qoh8552eu08d3p6wgz-de21ec5f.manus.computer/api/whatsapp/`
    *   **Nota:** Este URL é temporário. Para produção, utilize o URL da sua implantação permanente.
3.  **Validação de Pedidos (Recomendado):** Para segurança, configure a validação de pedidos da Twilio no seu endpoint Flask (`whatsapp.py`) utilizando o seu `TWILIO_AUTH_TOKEN`.

## Base de Dados

A tabela `reservations` tem a seguinte estrutura:

*   `id` (Integer, Primary Key)
*   `customer_name` (String)
*   `phone_number` (String)
*   `email` (String, Nullable)
*   `reservation_date` (Date)
*   `reservation_time` (Time)
*   `party_size` (Integer)
*   `status` (String, default: 'confirmed')
*   `channel` (String - 'web' ou 'whatsapp')
*   `created_at` (DateTime)
*   `updated_at` (DateTime)

## APIs

*   **POST /api/reservations/**: Cria uma nova reserva.
    *   Payload: JSON com os campos da reserva (excluindo id, status, created_at, updated_at).
*   **GET /api/reservations/**: Lista todas as reservas.
*   **GET /api/reservations/<id>**: Obtém detalhes de uma reserva específica.
*   **PUT/PATCH /api/reservations/<id>**: Atualiza uma reserva.
*   **DELETE /api/reservations/<id>**: Cancela uma reserva (marca o status como 'cancelled').
*   **POST /api/chat/**: Processa uma mensagem do widget web.
    *   Payload: `{"user_id": "some_id", "message": "user message"}`
    *   Resposta: `{"response": "bot response"}`
*   **POST /api/whatsapp/**: Webhook para mensagens WhatsApp (formato TwiML).


