from flask import Blueprint, request, jsonify
from ..models.booking import Booking, db # Changed to relative import
from ..utils.auth import token_required # Changed to relative import
from datetime import datetime # Added import for datetime parsing

booking_bp = Blueprint('booking', __name__, url_prefix='/api/booking')

@booking_bp.route('/', methods=['GET'])
@token_required
def list_bookings():
    try:
        bookings = Booking.query.all()
        return jsonify([b.serialize() for b in bookings]), 200
    except Exception:
        return jsonify({'error': 'Erro ao listar agendamentos.'}), 500

@booking_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_booking(id):
    try:
        booking = Booking.query.get_or_404(id)
        return jsonify(booking.serialize()), 200
    except Exception:
        return jsonify({'error': 'Erro ao buscar agendamento.'}), 500

@booking_bp.route('/', methods=['POST'])
@token_required
def create_booking():
    try:
        data = request.json
        new_booking = Booking(
            patient_id=request.user_id,
            professional_id=data['professional_id'],
            date_time=datetime.fromisoformat(data['scheduled_date']), # Corrected field name and parse string to datetime
            status=data.get('status', 'pending')
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify(new_booking.serialize()), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar agendamento.'}), 500

@booking_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_booking(id):
    try:
        booking = Booking.query.get_or_404(id)
        data = request.json
        if 'scheduled_date' in data: # Check if scheduled_date is provided for update
            booking.date_time = datetime.fromisoformat(data['scheduled_date']) # Update date_time field
        booking.status = data.get('status', booking.status)
        db.session.commit()
        return jsonify(booking.serialize()), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar agendamento.'}), 500

@booking_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_booking(id):
    try:
        booking = Booking.query.get_or_404(id)
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Agendamento deletado com sucesso.'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar agendamento.'}), 500
