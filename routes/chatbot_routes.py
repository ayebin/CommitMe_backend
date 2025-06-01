from flask import Blueprint, request, jsonify, Response
from sqlalchemy.sql import exists
from models import db, Session, Message, Sender, Info, Report
from datetime import datetime
from chatbot import gen_q_response, qna_response, feedback_response, report_response, ground_truth_answer
import json
import re

chat_bp = Blueprint('chat_bp', __name__)

# info global 저장.
info_cache = {}
parent_id = {}
question_cache = {}
global_q_index = 1
is_gen_q = True

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
    
    if session_id not in info_cache:
        info = Info.query.filter_by(info_id=info_id).first()
        info_cache[session_id] = {
            'position': info.position,
            'interest': info.interest,
            'history': info.history,
            'language': info.language,
            'project': info.project,
            'resume': info.resume,
        }

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
    
    #response = qna_response(info_cache, session_id, role, message, temperature, max_token)
    response = 'Hello test test test test test test test test test test test test test test test test test test test test'
    
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

def parse_questions(text: str) -> dict:
    pattern = r"- 질문\s*(\d+)\s*:\s*(.+)"
    matches = re.findall(pattern, text)
    return {num: question.strip() for num, question in matches}

@chat_bp.route('/question', methods=['POST'])
def generate_question():
    global question_cache, global_q_index, is_gen_q
    
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
    
    # if is_gen_q == True:
    #     question_cache = {}
    #     response = gen_q_response(info_cache, session_id, role)
    #     #print(f'LLM 질문 전체 response: {response}')  # 이미 string임
    #     question_cache = parse_questions(response)
    #     #print(f'question_cache after parse: {question_cache}')
    #     is_gen_q = False
    
    # current_q = question_cache.get(str(global_q_index))
    # if not current_q:
    #     return jsonify({'error': '질문이 없습니다.'}), 400
    
    if session_id in parent_id:
        temp = parent_id[session_id]
    else:
        temp = 1  # 혹은 적절한 기본값
    current_q = f'temporary question {temp} test test test test test test test test test test test test test test test test test test test test test test test test test test test'
    
    interview_question = Message(
        session_id = session_id,
        info_id = info_id,
        id = user_id,
        parent_id = None,
        sender = Sender.system,
        message_type = 'interview_q',
        content = current_q,
        role = role
    )
    db.session.add(interview_question)
    db.session.commit()
    
    parent_id[session_id] = interview_question.message_id
    global_q_index += 1
    if global_q_index > 10:
        is_gen_q = True
        global_q_index = 1
    
    return jsonify({'question': current_q})
    
    
@chat_bp.route('/feedback', methods=['POST'])
def generate_feedback():
    data = request.json
    user_id = data.get('user_id')
    info_id = data.get('info_id')
    session_id = data.get('session_id')
    final_answer = data.get('final_answer')
    role = data.get('role')
    feedbackLength = data.get('feedbackLength')  # max_token
    feedbackType = data.get('feedbackType')      # temperature

    # info_cache 없을 시 불러오기
    if session_id not in info_cache:
        info = Info.query.filter_by(info_id=info_id).first()
        info_cache[session_id] = {
            'position': info.position,
            'interest': info.interest,
            'history': info.history,
            'language': info.language,
            'project': info.project,
            'resume': info.resume,
        }

    # temperature 세팅
    if feedbackType == '균형 잡힌 답변':
        temperature = 0.5
    elif feedbackType == '차분한 답변':
        temperature = 0.2
    else:
        temperature = 0.8

    # max_token 세팅
    if feedbackLength == '기본':
        max_token = 500
    elif feedbackLength == '간결':
        max_token = 250
    else:
        max_token = 800
    
    print("parent_id:", parent_id)
    print("session_id:", session_id)
    print("parent_id[session_id]:", parent_id.get(session_id))
    
    # 마지막 질문 가져오기
    interview_question = Message.query.filter_by(
        message_id=parent_id[session_id],
        message_type='interview_q'
    ).first()

    # 사용자 최종 답변 저장
    final_message = Message(
        session_id=session_id,
        info_id=info_id,
        id=user_id,
        parent_id=parent_id[session_id],
        sender=Sender.user,
        message_type='fin_response',
        content=final_answer,
        role=role,
        temperature=temperature,
        max_token=max_token,
        quality=None
    )
    db.session.add(final_message)
    db.session.commit()

    # 현재 parent id -> message db -> parent_id에 해당하는 지문 가져오기. 
    gt = ground_truth_answer(info_cache, session_id, interview_question.content, temperature, max_token)
    
    # ✅ LLM 호출
    # feedback_text, quality = feedback_response(
    #     interview_question.content,
    #     gt,
    #     final_answer,
    #     info_cache,
    #     session_id,
    #     role,
    #     temperature,
    #     max_token
    # )
    feedback_text, quality = 'temporary feedback', None

    # 피드백 저장
    feedback_message = Message(
        session_id=session_id,
        info_id=info_id,
        id=user_id,
        parent_id=parent_id[session_id],
        sender=Sender.system,
        message_type='feedback',
        content=feedback_text,
        role=role,
        temperature=temperature,
        max_token=max_token,
        quality=quality
    )
    db.session.add(feedback_message)
    db.session.commit()

    return jsonify({'feedback': feedback_text, 'quality': quality}), 200  # ✅ 프론트에 quality까지 전달


def parse_report_sections(report_text):
    import re

    pattern = re.compile(r'^\s*\[(.+?)\]\s*\n([\s\S]+?)(?=\n\s*\[|$)', re.MULTILINE)
    sections = dict(re.findall(pattern, report_text))

    return {
        'expression': sections.get('언어적 표현 특징', '').strip(),
        'weak': sections.get('취약 부분', '').strip(),
        'fix': sections.get('개선해야 할 점', '').strip(),
        'score': sections.get('면접 대비 정도 추이', '').strip(),
    }

@chat_bp.route('/report', methods=['POST'])
def comprehensive_report():
    data = request.json
    user_id = data['user_id']
    session_id = data['session_id']
    info_id = data['info_id']
    role = data['role']
    feedbackLength = data['feedbackLength']
    feedbackType = data['feedbackType']
    
    if session_id not in info_cache:
        info = Info.query.filter_by(info_id=info_id).first()
        info_cache[session_id] = {
            'position': info.position,
            'interest': info.interest,
            'history': info.history,
            'language': info.language,
            'project': info.project,
            'resume': info.resume,
        }
        
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
        
    cache = []
    interview_qs = (
        Message.query
        .filter_by(session_id=session_id, message_type='interview_q')
        .order_by(Message.message_id.asc())
        .limit(10)
        .all()
    )

    for q in interview_qs:
        user_response = Message.query.filter_by(parent_id=q.message_id, message_type='question').first()
        feedback = Message.query.filter_by(parent_id=q.message_id, message_type='feedback').first()
        #quality = Message.query.filter_by(parent_id=q.message_id, message_type = )

        cache.append({
            'interview_question': q.content,
            'user_response': user_response.content if user_response else '',
            'feedback': feedback.content if feedback else '',
        })
        
    #report = report_response(cache, info_cache, user_id, session_id, info_id, role, max_token, temperature)
    report = """
        [언어적 표현 특징]
        문장이 명확하고 핵심을 잘 전달함
        일관된 어조와 전문성을 유지함

        [취약 부분]
        일부 질문에 대한 기술적 깊이가 부족함
        구체적인 사례나 수치 제시가 아쉬움

        [개선해야 할 점]
        프로젝트 중심의 경험을 더 부각시키고, 관련 기술을 명확히 설명할 것
        STAR 기법을 활용하여 구조적인 답변을 연습할 것

        [면접 대비 정도 추이]
        기본기는 탄탄하나, 실무 중심의 경험과 문제 해결 능력 표현이 강화되면 실전 면접에서 높은 평가 가능
    """
    
    # report DB 저장
    
    # 파싱
    parsed = parse_report_sections(report)

    # DB 저장
    new_report = Report(
        session_id=session_id,
        info_id=info_id,
        id=user_id,
        expression=parsed['expression'],
        weak=parsed['weak'],
        fix=parsed['fix'],
        score=parsed['score'],
    )

    db.session.add(new_report)
    db.session.commit()
    
    return jsonify({'report': report}), 200