from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.booking import Booking
from src.models.professional import Professional
from src.utils.auth import token_required
from datetime import datetime

booking_bp = Blueprint('booking', __name__, url_prefix='/api/booking')


@booking_bp.route("/", methods=['POST'])
@token_required
def create_booking():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid input"}), 400

    if request.user_type != 'patient':
        return jsonify({"message": "Only patients can create bookings"}), 403

    professional_id = data.get('professional_id')
    scheduled_date_str = data.get('scheduled_date')

    if not all([professional_id, scheduled_date_str]):
        return jsonify({"message": "Missing professional_id or scheduled_date"}), 400

    professional = Professional.query.join(User, User.id == Professional.user_id).filter(Professional.id == professional_id, User.approval_status == 'approved').first()
    if not professional:
        return jsonify({"message": "Professional not found or not approved"}), 404

    try:
        # Ensure scheduled_date_str is not empty before parsing
        if not scheduled_date_str.strip():
            return jsonify({"message": "scheduled_date cannot be empty"}), 400
        scheduled_date = datetime.fromisoformat(scheduled_date_str)
        if scheduled_date < datetime.utcnow():
            return jsonify({"message": "Scheduled date must be in the future"}), 400
    except ValueError:
        return jsonify({"message": "Invalid date format for scheduled_date. Use YYYY-MM-DDTHH:MM:SS"}), 400
    except Exception as e: # Catch other potential errors during date parsing
        return jsonify({"message": f"Error processing scheduled_date: {str(e)}"}), 400


    try:
        new_booking = Booking(
            patient_id=request.user_id, # This comes from @token_required
            professional_id=professional_id,
            scheduled_date=scheduled_date,
            status='pending'
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify(new_booking.serialize()), 201
    except Exception as e:
        db.session.rollback()
        # Consider logging the error e for debugging
        return jsonify({"message": "Could not create booking", "error": str(e)}), 500

@booking_bp.route("/", methods=['GET'])
@token_required
def get_bookings():
    try:
        if request.user_type == 'patient':
            bookings = Booking.query.filter_by(patient_id=request.user_id).all()
        elif request.user_type == 'professional':
            bookings = Booking.query.filter_by(professional_id=request.user_id).all()
        elif request.user_type == 'admin':
            bookings = Booking.query.all()
        else:
            # This case should ideally not be reached if user_type is always set by @token_required
            return jsonify({"message": "Invalid user type"}), 403
        
        return jsonify([booking.serialize() for booking in bookings]), 200
    except Exception as e:
        # Consider logging the error e
        return jsonify({"message": "Could not retrieve bookings", "error": str(e)}), 500

@booking_bp.route("/<int:booking_id>/status", methods=['PATCH'])
@token_required
def update_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get('status')

    if not new_status:
        return jsonify({"message": "Missing status in request body"}), 400

    allowed_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
    if new_status not in allowed_statuses:
        return jsonify({"message": f"Invalid status. Allowed statuses are: {', '.join(allowed_statuses)}"}), 400

    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"message": "Booking not found"}), 404

        original_status = booking.status

        # Authorization and logic
        if request.user_type == 'professional':
            if booking.professional_id != request.user_id:
                return jsonify({"message": "Professional not authorized to update this booking"}), 403
            if new_status not in ['confirmed', 'cancelled', 'completed']: # Professionals can also mark as completed
                return jsonify({"message": f"Professional cannot set status to '{new_status}'"}), 403
            # Professionals can complete a confirmed booking
            if new_status == 'completed' and original_status != 'confirmed':
                 return jsonify({"message": "Only confirmed bookings can be marked as completed by professionals"}), 403

        elif request.user_type == 'patient':
            if booking.patient_id != request.user_id:
                return jsonify({"message": "Patient not authorized to update this booking"}), 403
            if new_status != 'cancelled':
                return jsonify({"message": "Patient can only cancel bookings"}), 403
            if original_status not in ['pending', 'confirmed']:
                return jsonify({"message": f"Booking with status '{original_status}' cannot be cancelled by patient"}), 403
        
        elif request.user_type == 'admin': # Admins can update to any valid status
            pass # No specific restriction for admin beyond allowed_statuses

        else:
            return jsonify({"message": "User type not authorized for this action"}), 403

        booking.status = new_status
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify(booking.serialize()), 200

    except Exception as e:
        db.session.rollback()
        # Consider logging the error e
        return jsonify({"message": "Could not update booking status", "error": str(e)}), 500
