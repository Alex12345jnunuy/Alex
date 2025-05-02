from flask import Blueprint, request, Response
from twilio.twiml.messaging_response import MessagingResponse
import logging
import requests # To call the internal chat logic API
import os

whatsapp_bp = Blueprint("whatsapp_bp", __name__)

logging.basicConfig(level=logging.INFO)

# In-memory store for conversation state (simple example, replace with DB/Redis for production)
# This state should ideally be shared or managed centrally with the web chat
conversation_states_whatsapp = {}

# Function to call the internal chat logic (refactoring needed)
def get_bot_response(user_id, message):
    # For now, let's call the existing /api/chat endpoint internally
    # This is not ideal, refactoring chat logic is better
    try:
        api_url = "http://localhost:5000/api/chat" # Assuming the app runs on port 5000
        payload = {"user_id": user_id, "message": message}
        response = requests.post(api_url, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        return data.get("response", "Desculpe, ocorreu um erro.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling internal chat API: {e}")
        return "Desculpe, não consigo processar o seu pedido neste momento."

@whatsapp_bp.route("/", methods=["POST"])
def handle_whatsapp_message():
    incoming_msg = request.values.get("Body", "").strip()
    sender_phone = request.values.get("From", "") # Format: whatsapp:+14155238886
    
    logging.info(f"Received WhatsApp message from {sender_phone}: {incoming_msg}")

    if not sender_phone or not incoming_msg:
        logging.warning("Missing sender phone or message body in WhatsApp request")
        return Response(status=400)

    # Use phone number as user_id for state management
    user_id = sender_phone

    # Get response from chat logic
    bot_reply = get_bot_response(user_id, incoming_msg)

    # Create TwiML response
    twiml_response = MessagingResponse()
    twiml_response.message(bot_reply)

    logging.info(f"Sending WhatsApp reply to {sender_phone}: {bot_reply}")

    return Response(str(twiml_response), mimetype="application/xml")

# TODO: Secure this endpoint, e.g., using Twilio request validation
# TODO: Refactor chat logic to be shared between web and WhatsApp
# TODO: Integrate actual reservation API call in chat logic

