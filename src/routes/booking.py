from flask import Blueprint, request, jsonify
from src.models.booking import Booking, db
from src.utils.auth import token_required
from datetime import datetime

booking_bp = Blueprint('booking', __name__, url_prefix='/api/booking')

@booking_bp.route('/', methods=['GET'])
@token_required
def list_bookings():
    try:
        bookings = Booking.query.all()
        return jsonify([b.serialize() for b in bookings]), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao listar agendamentos: {str(e)}'}), 500

@booking_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_booking(id):
    try:
        booking = Booking.query.get_or_404(id)
        return jsonify(booking.serialize()), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar agendamento: {str(e)}'}), 500

@booking_bp.route('/', methods=['POST'])
@token_required
def create_booking():
    try:
        data = request.json
        new_booking = Booking(
            patient_id=request.user_id,
            professional_id=data['professional_id'],
            scheduled_date=datetime.fromisoformat(data['scheduled_date']),
            status=data.get('status', 'pending')
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify(new_booking.serialize()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar agendamento: {str(e)}'}), 500

@booking_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_booking(id):
    try:
        booking = Booking.query.get_or_404(id)
        data = request.json
        if 'scheduled_date' in data:
            booking.scheduled_date = datetime.fromisoformat(data['scheduled_date'])
        booking.status = data.get('status', booking.status)
        db.session.commit()
        return jsonify(booking.serialize()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar agendamento: {str(e)}'}), 500

@booking_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_booking(id):
    try:
        booking = Booking.query.get_or_404(id)
        db.session.delete(booking)
        db.session.commit()
        return jsonify({'message': 'Agendamento deletado com sucesso.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar agendamento: {str(e)}'}), 500
