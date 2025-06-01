from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from models import db, Info
import os
from flask_cors import cross_origin
from ocr.ocr import extract_text
from sum_llm import summarize_resume

info_bp = Blueprint('info_bp', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'jpeg', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@info_bp.route('/add_info', methods=['POST', 'OPTIONS'])
@cross_origin()
def add_info():
    try:
        user_id_str = request.form.get('user_id')
        if not user_id_str:
            return jsonify({'error': 'user_id is required'}), 400
        try:
            user_id = int(user_id_str)
        except ValueError:
            return jsonify({'error': 'user_id must be an integer'}), 400
        
        position = request.form.get('position')
        interest = request.form.get('interest')
        history = request.form.get('history')
        language = request.form.get('language')
        project = request.form.get('project')

        # 2) 파일 받기
        file = request.files.get('resume')

        resume_text = None
        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(save_path)
                # OCR 처리
                extracted_text = extract_text(save_path)
                # LLM 요약
                resume_text = summarize_resume(extracted_text)
            else:
                return jsonify({'error': '지원하지 않는 파일 형식입니다.'}), 400
        else:
            resume_text = None  # 파일이 없어도 괜찮은 경우

        info = Info(
                    id=user_id,
                    position=position,
                    interest=interest,
                    history=history,
                    language=language,
                    project=project,
                    resume=resume_text
                )
        
        db.session.add(info)
        db.session.commit()
        
        return jsonify({'info_id': info.info_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    