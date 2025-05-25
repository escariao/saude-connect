from flask import Blueprint, request, jsonify
from src.models.booking import Booking, db
from src.utils.auth import token_required

booking_bp = Blueprint('booking', __name__, url_prefix='/api/booking')


@booking_bp.route('/', methods=['GET'])
@token_required
def list_bookings():
    """Listar todos os agendamentos."""
    bookings = Booking.query.all()
    return jsonify([b.serialize() for b in bookings]), 200


@booking_bp.route('/<int:id>', methods=['GET'])
@token_required
def get_booking(id):
    """Consultar um agendamento específico pelo ID."""
    booking = Booking.query.get_or_404(id)
    return jsonify(booking.serialize()), 200


@booking_bp.route('/', methods=['POST'])
@token_required
def create_booking():
    """Criar um novo agendamento."""
    data = request.json
    new_booking = Booking(
        patient_id=request.user_id,
        professional_id=data['professional_id'],
        scheduled_date=data['scheduled_date'],
        status=data.get('status', 'pending')
    )
    db.session.add(new_booking)
    db.session.commit()
    return jsonify(new_booking.serialize()), 201


@booking_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_booking(id):
    """Atualizar um agendamento existente."""
    booking = Booking.query.get_or_404(id)
    data = request.json
    booking.scheduled_date = data.get('scheduled_date', booking.scheduled_date)
    booking.status = data.get('status', booking.status)
    db.session.commit()
    return jsonify(booking.serialize()), 200


@booking_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_booking(id):
    """Excluir um agendamento pelo ID."""
    booking = Booking.query.get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    return jsonify({'message': 'Booking deletado'}), 200
