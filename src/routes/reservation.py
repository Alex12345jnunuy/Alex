from flask import Blueprint, request, jsonify
from src.models.reservation import db, Reservation
from datetime import datetime
import logging

reservation_bp = Blueprint("reservation_bp", __name__)

logging.basicConfig(level=logging.INFO)

@reservation_bp.route("/", methods=["POST"])
def create_reservation():
    data = request.get_json()
    logging.info(f"Received reservation request: {data}")

    required_fields = ["customer_name", "phone_number", "reservation_date", "reservation_time", "party_size", "channel"]
    if not data or not all(field in data for field in required_fields):
        logging.warning("Missing required fields in request")
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Basic validation and type conversion
        reservation_date = datetime.strptime(data["reservation_date"], "%Y-%m-%d").date()
        reservation_time = datetime.strptime(data["reservation_time"], "%H:%M").time()
        party_size = int(data["party_size"])
        customer_name = str(data["customer_name"])
        phone_number = str(data["phone_number"])
        email = data.get("email") # Optional
        channel = str(data["channel"])

        if party_size <= 0:
             logging.warning("Invalid party size")
             return jsonify({"error": "Party size must be positive"}), 400

        # TODO: Add more validation (e.g., check date/time is in the future, check availability)

        new_reservation = Reservation(
            customer_name=customer_name,
            phone_number=phone_number,
            email=email,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            party_size=party_size,
            channel=channel,
            status='confirmed' # Defaulting to confirmed for now
        )

        db.session.add(new_reservation)
        db.session.commit()
        logging.info(f"Reservation created successfully: ID {new_reservation.id}")

        return jsonify({
            "message": "Reservation created successfully",
            "reservation_id": new_reservation.id
        }), 201

    except ValueError as ve:
        logging.error(f"Value error during reservation creation: {ve}")
        db.session.rollback()
        return jsonify({"error": f"Invalid data format: {ve}"}), 400
    except Exception as e:
        logging.error(f"Error creating reservation: {e}")
        db.session.rollback()
        return jsonify({"error": "An internal error occurred"}), 500

# TODO: Add endpoints for GET (list/details), PUT/PATCH (update), DELETE (cancel)




@reservation_bp.route("/", methods=["GET"])
def get_reservations():
    try:
        # TODO: Add filtering/pagination if needed
        reservations = Reservation.query.all()
        result = []
        for res in reservations:
            result.append({
                "id": res.id,
                "customer_name": res.customer_name,
                "phone_number": res.phone_number,
                "email": res.email,
                "reservation_date": res.reservation_date.isoformat(),
                "reservation_time": res.reservation_time.isoformat(),
                "party_size": res.party_size,
                "status": res.status,
                "channel": res.channel,
                "created_at": res.created_at.isoformat(),
                "updated_at": res.updated_at.isoformat()
            })
        logging.info(f"Retrieved {len(result)} reservations")
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error retrieving reservations: {e}")
        return jsonify({"error": "An internal error occurred"}), 500

@reservation_bp.route("/<int:reservation_id>", methods=["GET"])
def get_reservation_by_id(reservation_id):
    try:
        reservation = Reservation.query.get(reservation_id)
        if reservation:
            result = {
                "id": reservation.id,
                "customer_name": reservation.customer_name,
                "phone_number": reservation.phone_number,
                "email": reservation.email,
                "reservation_date": reservation.reservation_date.isoformat(),
                "reservation_time": reservation.reservation_time.isoformat(),
                "party_size": reservation.party_size,
                "status": reservation.status,
                "channel": reservation.channel,
                "created_at": reservation.created_at.isoformat(),
                "updated_at": reservation.updated_at.isoformat()
            }
            logging.info(f"Retrieved reservation ID {reservation_id}")
            return jsonify(result), 200
        else:
            logging.warning(f"Reservation ID {reservation_id} not found")
            return jsonify({"error": "Reservation not found"}), 404
    except Exception as e:
        logging.error(f"Error retrieving reservation ID {reservation_id}: {e}")
        return jsonify({"error": "An internal error occurred"}), 500




@reservation_bp.route("/<int:reservation_id>", methods=["PUT", "PATCH"])
def update_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        logging.warning(f"Update attempt for non-existent reservation ID {reservation_id}")
        return jsonify({"error": "Reservation not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    try:
        # Update fields if provided in the request
        if "customer_name" in data:
            reservation.customer_name = str(data["customer_name"])
        if "phone_number" in data:
            reservation.phone_number = str(data["phone_number"])
        if "email" in data:
            reservation.email = str(data["email"])
        if "reservation_date" in data:
            reservation.reservation_date = datetime.strptime(data["reservation_date"], "%Y-%m-%d").date()
        if "reservation_time" in data:
            reservation.reservation_time = datetime.strptime(data["reservation_time"], "%H:%M").time()
        if "party_size" in data:
            party_size = int(data["party_size"])
            if party_size <= 0:
                raise ValueError("Party size must be positive")
            reservation.party_size = party_size
        if "status" in data:
            reservation.status = str(data["status"])

        db.session.commit()
        logging.info(f"Reservation ID {reservation_id} updated successfully")
        return jsonify({"message": "Reservation updated successfully"}), 200

    except ValueError as ve:
        logging.error(f"Value error during reservation update for ID {reservation_id}: {ve}")
        db.session.rollback()
        return jsonify({"error": f"Invalid data format: {ve}"}), 400
    except Exception as e:
        logging.error(f"Error updating reservation ID {reservation_id}: {e}")
        db.session.rollback()
        return jsonify({"error": "An internal error occurred"}), 500

@reservation_bp.route("/<int:reservation_id>", methods=["DELETE"])
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        logging.warning(f"Cancel attempt for non-existent reservation ID {reservation_id}")
        return jsonify({"error": "Reservation not found"}), 404

    try:
        # Option 1: Actually delete the record
        # db.session.delete(reservation)

        # Option 2: Mark as cancelled (preferred for history)
        reservation.status = "cancelled"
        db.session.commit()
        logging.info(f"Reservation ID {reservation_id} marked as cancelled")
        return jsonify({"message": "Reservation cancelled successfully"}), 200

    except Exception as e:
        logging.error(f"Error cancelling reservation ID {reservation_id}: {e}")
        db.session.rollback()
        return jsonify({"error": "An internal error occurred"}), 500

