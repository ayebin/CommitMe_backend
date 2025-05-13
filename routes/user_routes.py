from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db 

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/add_user', methods=['POST'])
def add_user():
    try:
        user = User() # auto_increment
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'user_id': user.id}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    