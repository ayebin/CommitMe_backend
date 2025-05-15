from flask import Blueprint, jsonify, request
from models import db, Session
from datetime import datetime

session_bp = Blueprint('session_bp', __name__)

@session_bp.route('/add_session', methods=['POST'])
def add_session():
    try:
        data = request.get_json()
        new_session = Session(
            id=data['user_id'],
            info_id=data['info_id']
        )
        db.session.add(new_session)
        db.session.commit()

        return jsonify({'session_id': new_session.session_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    