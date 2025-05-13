from flask import Blueprint, jsonify, request
from models import db, Info
from flask_cors import cross_origin

info_bp = Blueprint('info_bp', __name__)

@info_bp.route('/add_info', methods=['POST', 'OPTIONS'])
@cross_origin()
def add_info():
    try:
        data = request.get_json()

        info = Info(
            id=data['user_id'],
            position=data['position'],
            interest=data['interest'],
            history=data['history'],
            language=data['language'],
            project=data['project'],
            resume=None  # 추후 확장 
        )
        
        db.session.add(info)
        db.session.commit()
        
        return jsonify({'info_id': info.info_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500