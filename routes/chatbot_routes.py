from flask import Blueprint, request, jsonify
from sqlalchemy.sql import exists
from models import db, Session, Message, Sender, Info
from datetime import datetime
from chatbot import get_response

chat_bp = Blueprint('chat_bp', __name__)

# info global 저장.
info_cache = {}

@chat_bp.route('/chatting', methods=['POST'])
def send_message():
    data = request.get_json()

    message = data.get('message')
    user_id = data.get('user_id')
    info_id = data.get('info_id')
    session_id = data.get('session_id')
    role = data.get('role')  # 면접관 성격
    feedbackLength = data.get('feedbackLength')  # max_token
    feedbackType = data.get('feedbackType')      # temperature

    # 값 매핑
    if feedbackType == '균형 잡힌 답변':
        temperature = 0.5
    elif feedbackType == '차분한 답변':
        temperature = 0.2
    else:
        temperature == 0.8
        
    if feedbackLength == '기본':
        max_token = 500
    elif feedbackLength == '간결한 답변':
        max_token = 250
    else: 
        max_token = 800
        
        
    latest_bot_message = Message.query.filter_by(
        session_id=session_id,
        sender=Sender.system
    ).order_by(Message.message_id.desc()).first()

    user_parent_id = latest_bot_message.message_id if latest_bot_message else None


    # message 저장
    user_message = Message(
        session_id=session_id,
        id=user_id,
        info_id=info_id,
        sender=Sender.user,
        parent_id = user_parent_id,
        content=message,
        role=role,
        temperature=temperature,
        max_token=max_token,
        quality = None # 임시
    )
    db.session.add(user_message)
    db.session.commit()

    # user_id로 정보 가져오기
    if session_id not in info_cache and user_parent_id is None:
        info = Info.query.filter_by(info_id=info_id).first()
        info_cache[session_id] = {
            'position': info.position,
            'interest': info.interest,
            'history': info.history,
            'language': info.language,
            'project': info.project,
            'resume': info.resume,
        }
        
    # print(info_cache[session_id]['position']) 확인용

    
    #response = get_response(info_cache, session_id, role, message, temperature, max_token)
    response = 'Hello'
    
    bot_message = Message(
        session_id = session_id,
        id = user_id,
        info_id = info_id,
        sender = Sender.system,
        parent_id = user_message.message_id,
        content = response,
        quality = None, # 나중에 이것도 수정
    )
    db.session.add(bot_message)
    db.session.commit()

    # 임시 응답
    return jsonify({'response': 'Hello'}), 200