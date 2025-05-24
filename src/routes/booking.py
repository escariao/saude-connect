# src/routes/booking.py

from flask import Blueprint, request, jsonify
from src.models.booking import Booking, db

booking_bp = Blueprint('booking', __name__, url_prefix='/api/booking')

@booking_bp.route('/', methods=['GET'])
def list_bookings():
    bookings = Booking.query.all()
    return jsonify([b.serialize() for b in bookings]), 200

@booking_bp.route('/<int:id>', methods=['GET'])
def get_booking(id):
    booking = Booking.query.get_or_404(id)
    return jsonify(booking.serialize()), 200

@booking_bp.route('/', methods=['POST'])
def create_booking():
    data = request.json
    new_booking = Booking(
        patient_id=data['patient_id'],
        professional_id=data['professional_id'],
        scheduled_date=data['scheduled_date'],
        status=data.get('status', 'pending')
    )
    db.session.add(new_booking)
    db.session.commit()
    return jsonify(new_booking.serialize()), 201

@booking_bp.route('/<int:id>', methods=['PUT'])
def update_booking(id):
    booking = Booking.query.get_or_404(id)
    data = request.json
    booking.scheduled_date = data.get('scheduled_date', booking.scheduled_date)
    booking.status = data.get('status', booking.status)
    db.session.commit()
    return jsonify(booking.serialize()), 200

@booking_bp.route('/<int:id>', methods=['DELETE'])
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    return jsonify({'message': 'Booking deleted'}), 200
