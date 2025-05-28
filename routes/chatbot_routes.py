from flask import Blueprint, request, jsonify, Response
from sqlalchemy.sql import exists
from models import db, Session, Message, Sender, Info
from datetime import datetime
from chatbot import gen_q_response
import json

chat_bp = Blueprint('chat_bp', __name__)

# info global 저장.
info_cache = {}
parent_id = {}

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
    elif feedbackLength == '간결':
        max_token = 250
    else: 
        max_token = 800
        
    # message 저장
    user_message = Message(
        session_id=session_id,
        info_id=info_id,
        id=user_id,
        parent_id = parent_id[session_id],
        sender=Sender.user,
        message_type = 'question',
        content=message,
        role=role,
        temperature=temperature,
        max_token=max_token,
        quality = None 
    )
    db.session.add(user_message)
    db.session.commit()
        
    # print(info_cache[session_id]['position']) 확인용
    
    #response = get_response(info_cache, session_id, role, message, temperature, max_token)
    response = 'Hello'
    
    bot_message = Message(
        session_id = session_id,
        info_id = info_id,
        id = user_id,
        parent_id = parent_id[session_id],
        sender = Sender.system,
        message_type = 'answer',
        content = response,
        role=role,
        temperature=temperature,
        max_token=max_token,
        quality = None, # 나중에 이것도 수정
    )
    db.session.add(bot_message)
    db.session.commit()

    # 임시 응답
    return jsonify({'response': response}), 200

@chat_bp.route('/question', methods=['POST'])
def generate_question():
    data = request.json
    
    message = data.get('message')
    user_id = data.get('user_id')
    info_id = data.get('info_id')
    session_id = data.get('session_id')
    role = data.get('role')
    
    latest_bot_message = Message.query.filter_by(
        session_id=session_id,
        sender=Sender.system
    ).order_by(Message.message_id.desc()).first()

    user_parent_id = latest_bot_message.message_id if latest_bot_message else None

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
        
    #response = qna_response(info_cache, session_id, role)
    if session_id in parent_id:
        temp = parent_id[session_id]
    else:
        temp = 1  # 혹은 적절한 기본값
    response = f'temporary question {temp}'
    
    interview_question = Message(
        session_id = session_id,
        info_id = info_id,
        id = user_id,
        parent_id = None,
        sender = Sender.system,
        message_type = 'interview_q',
        content = response,
        role = role
    )
    db.session.add(interview_question)
    db.session.commit()
    
    parent_id[session_id] = interview_question.message_id
    
    return Response(
    json.dumps({'question': response}, ensure_ascii=False),
    mimetype='application/json'
)