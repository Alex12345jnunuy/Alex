from flask import Blueprint, request, jsonify
import logging
import requests # Added for internal API call
import os # Added for getting base URL

chat_bp = Blueprint("chat_bp", __name__)

logging.basicConfig(level=logging.INFO)

# In-memory store for conversation state (simple example, replace with DB/Redis for production)
conversation_states = {}

# Determine the base URL for internal API calls
BASE_URL = f"http://localhost:{os.getenv('PORT', 5000)}"

@chat_bp.route("/", methods=["POST"])
def handle_chat_message():
    data = request.get_json()
    user_id = data.get("user_id", "default_user") # Need a way to identify users
    message = data.get("message", "").lower()
    # Determine channel based on user_id prefix or another method
    channel = "web" if user_id.startswith("web_") else "unknown"
    logging.info(f"Received message from {user_id} via {channel}: {message}")

    # Get current state or initialize
    state = conversation_states.get(user_id, {"stage": "start", "details": {}})

    bot_response = "" # Initialize bot_response

    # Simple state machine for reservation
    if state["stage"] == "start":
        if "reserva" in message:
            bot_response = "Claro! Para começar, qual o seu nome?"
            state["stage"] = "get_name"
        else:
            bot_response = "Olá! Posso ajudar a fazer uma reserva no Pila."
    elif state["stage"] == "get_name":
        state["details"]["customer_name"] = message.title()
        bot_response = f"Obrigado, {state['details']['customer_name']}. Qual o seu número de telefone?"
        state["stage"] = "get_phone"
    elif state["stage"] == "get_phone":
        # TODO: Add phone number validation
        state["details"]["phone_number"] = message
        bot_response = "E o seu email (opcional)? Se não quiser fornecer, diga \"não\"."
        state["stage"] = "get_email"
    elif state["stage"] == "get_email":
        if message != "não":
            # TODO: Add email validation
            state["details"]["email"] = message
        else:
            state["details"]["email"] = None # Ensure email is None if not provided
        bot_response = "Para que dia gostaria de reservar? (Formato AAAA-MM-DD)"
        state["stage"] = "get_date"
    elif state["stage"] == "get_date":
        # TODO: Add date validation (ensure format and future date)
        state["details"]["reservation_date"] = message
        bot_response = "E a que horas? (Formato HH:MM, 24h)"
        state["stage"] = "get_time"
    elif state["stage"] == "get_time":
        # TODO: Add time validation (ensure format and valid time)
        state["details"]["reservation_time"] = message
        bot_response = "Para quantas pessoas?"
        state["stage"] = "get_party_size"
    elif state["stage"] == "get_party_size":
        try:
            party_size = int(message)
            if party_size <= 0:
                raise ValueError("Party size must be positive")
            state["details"]["party_size"] = party_size
            # All details collected, confirm?
            details = state["details"]
            email_text = f" (Email: {details['email']})" if details.get("email") else ""
            bot_response = f"Excelente. Confirma a reserva para {details['party_size']} pessoa(s) no dia {details['reservation_date']} às {details['reservation_time']} em nome de {details['customer_name']} (Contacto: {details['phone_number']}{email_text})? (sim/não)"
            state["stage"] = "confirm"
        except ValueError as e:
            logging.warning(f"Invalid party size input from {user_id}: {message} - {e}")
            bot_response = "Por favor, indique um número válido de pessoas (maior que zero)."
            # Stay in the same stage

    elif state["stage"] == "confirm":
        if message == "sim":
            try:
                reservation_payload = state["details"].copy()
                reservation_payload["channel"] = channel # Add channel info

                logging.info(f"Attempting to create reservation for {user_id} with payload: {reservation_payload}")

                # Call the reservation API endpoint
                reservation_api_url = f"{BASE_URL}/api/reservations/"
                logging.info(f"Calling reservation API: POST {reservation_api_url}") # Added log
                response = requests.post(reservation_api_url, json=reservation_payload)
                logging.info(f"Reservation API response status: {response.status_code}") # Added log
                logging.debug(f"Reservation API response text: {response.text}") # Added debug log

                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

                response_data = response.json()
                reservation_id = response_data.get("reservation_id")

                if reservation_id: # Check if ID was retrieved
                    bot_response = f"Reserva confirmada com sucesso! O ID da sua reserva é {reservation_id}. Obrigado."
                    logging.info(f"Reservation successful for {user_id}, ID: {reservation_id}")
                else:
                    # Handle case where API call succeeded but didn't return ID
                    logging.error(f"Reservation API call succeeded for {user_id} but no reservation_id returned. Response: {response_data}")
                    bot_response = "Reserva processada, mas houve um problema ao obter o ID. Por favor, contacte o restaurante para confirmar."

                # Reset state only on success or known handled failure
                state = {"stage": "start", "details": {}}

            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to create reservation for {user_id}. API call error: {e}")
                # Ensure bot_response is set in error cases too
                if e.response is not None:
                    try:
                        error_details = e.response.json()
                        bot_response = f"Desculpe, houve um erro ao criar a reserva: {error_details.get('error', 'Erro desconhecido do servidor')}. Por favor, tente novamente mais tarde."
                    except ValueError: # JSONDecodeError
                        bot_response = f"Desculpe, houve um erro ({e.response.status_code}) ao criar a reserva. Por favor, tente novamente mais tarde."
                else:
                    bot_response = "Desculpe, não foi possível conectar ao sistema de reservas. Por favor, tente novamente mais tarde."
                # Keep state for potential retry or correction? Let's reset for now.
                state = {"stage": "start", "details": {}}

            except Exception as e:
                 logging.error(f"Unexpected error during reservation confirmation for {user_id}: {e}")
                 bot_response = "Desculpe, ocorreu um erro inesperado. Por favor, tente novamente mais tarde."
                 # Reset state on unexpected error
                 state = {"stage": "start", "details": {}}

        elif message == "não":
            bot_response = "Reserva cancelada. Se precisar de algo mais, é só dizer."
            state = {"stage": "start", "details": {}}
        else:
            bot_response = "Por favor, responda \"sim\" para confirmar ou \"não\" para cancelar."
            # Stay in confirm stage

    # If bot_response is still empty, provide a default fallback
    if not bot_response and state['stage'] != 'confirm': # Avoid overriding specific confirm messages
         bot_response = "Desculpe, não entendi. Pode repetir?"
         logging.warning(f"Reached end of handler for {user_id} without setting bot_response. State: {state}, Message: {message}")

    # Save state
    conversation_states[user_id] = state

    logging.info(f"Final Bot response to {user_id}: {bot_response}") # Changed log message slightly
    return jsonify({"response": bot_response})

