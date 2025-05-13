from flask import Blueprint, jsonify, request
from models import db, Session
from datetime import datetime

session_bp = Blueprint('session_bp', __name__)

@session_bp.route('/add_session', methods=['POST'])
def add_session():
    try:
        session = Session() # auto_increment
        db.session.add(session)
        db.session.commit()
        
        return jsonify({'session_id': session.id}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    