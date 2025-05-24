
from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.booking import Booking

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/', methods=['POST'])
def create_booking():
    data = request.get_json()
    booking = Booking(
        patient_id=data['patient_id'],
        professional_id=data['professional_id'],
        date_time=data['date_time'],
        status=data.get('status', 'pendente')
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify({'message': 'Booking created', 'id': booking.id}), 201

@booking_bp.route('/', methods=['GET'])
def get_bookings():
    bookings = Booking.query.all()
    result = [{
        'id': b.id,
        'patient_id': b.patient_id,
        'professional_id': b.professional_id,
        'date_time': b.date_time.isoformat(),
        'status': b.status
    } for b in bookings]
    return jsonify(result), 200

@booking_bp.route('/<int:id>', methods=['GET'])
def get_booking(id):
    booking = Booking.query.get_or_404(id)
    result = {
        'id': booking.id,
        'patient_id': booking.patient_id,
        'professional_id': booking.professional_id,
        'date_time': booking.date_time.isoformat(),
        'status': booking.status
    }
    return jsonify(result), 200

@booking_bp.route('/<int:id>', methods=['PUT'])
def update_booking(id):
    booking = Booking.query.get_or_404(id)
    data = request.get_json()
    booking.date_time = data.get('date_time', booking.date_time)
    booking.status = data.get('status', booking.status)
    db.session.commit()
    return jsonify({'message': 'Booking updated'}), 200

@booking_bp.route('/<int:id>', methods=['DELETE'])
def delete_booking(id):
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    return jsonify({'message': 'Booking deleted'}), 200
