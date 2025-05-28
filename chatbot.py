import os
import requests
import json
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), 'api.env')
load_dotenv(dotenv_path)

API_KEY = os.getenv("PERPLEXITY_API_KEY")

url = "https://api.perplexity.ai/chat/completions"  
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

################## Q&A Model ################## 
def qna_model(info_cache, session_id, role, user, temperature, max_token):
    position = info_cache[session_id]['position']
    interest = info_cache[session_id]['interest']
    history = info_cache[session_id]['history']
    language = info_cache[session_id]['language']
    project = info_cache[session_id]['project']
    resume = info_cache[session_id]['resume']

    system_template = f'''
    당신은 개발 및 AI 분야의 면접을 대비하는 지원자의 면접 준비를 도와주는 도우미입니다. 
    면접관은 지원자의 역량, 문제 해결 능력, 기술 이해도, 협업 경험 등을 평가하기 위해 체계적이고 날카로운 질문을 합니다.
    지원자의 정보에 맞추어 지원자의 요청에 대한 적절한 응답으로 도움을 줍니다. 
    면접관의 면접 스타일은 {role}입니다. 이 스타일을 고려하여 지원자를 돕습니다.
    
    ### 사용자 정보:
    - 희망 직무: {position}
    - 현재 관심사: {interest}
    - 경력: {history}
    - 주로 사용하거나 사용할 수 있는 언어: {language}
    - 프로젝트 경험: {project}
    - 이력서 정보: {resume}
    '''
    
    data = {
    "model": "sonar",
    "messages": [
        {'role': 'system', 'content': system_template},
        {"role": "user", "content": user}
    ],
    "temperature": temperature,
    'max_tokens':  max_token
    }   
    
    return data


def qna_response(info_cache, session_id, role, user, temperature, max_token):
    response = requests.post(url, headers=headers, json = qna_model(info_cache, session_id, role, user, temperature, max_token))
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f'response.status_code, response.text'

################## Question Generation Model ################## 
def gen_q_model(info_cache, session_id, role):
    position = info_cache[session_id]['position']
    interest = info_cache[session_id]['interest']
    history = info_cache[session_id]['history']
    language = info_cache[session_id]['language']
    project = info_cache[session_id]['project']
    resume = info_cache[session_id]['resume']

    system_template = f'''
    당신은 개발 및 AI 분야에 특화된 면접관입니다. 
    지원자의 역량, 문제 해결 능력, 기술 이해도, 협업 경험 등을 평가하기 위해 체계적이고 날카로운 질문을 합니다.
    질문은 사용자의 정보에 맞춤형으로 이루어져야 하며, 실제 기업 면접과 유사한 수준의 깊이를 지닙니다. 
    당신의 면접 스타일은 {role}입니다. 이 스타일에 충실하여 사용자 맞춤형 질문을 제시합니다.
    질문의 길이는 길지 않아야 합니다.
    
    ### 사용자 정보:
    - 희망 직무: {position}
    - 현재 관심사: {interest}
    - 경력: {history}
    - 주로 사용하거나 사용할 수 있는 언어: {language}
    - 프로젝트 경험: {project}
    - 이력서 정보: {resume}
    '''
    
    data = {
    "model": "sonar",
    "messages": [
        {'role': 'system', 'content': system_template},
        {"role": "user", "content": '질문을 생성해줘'}
    ],
    }   
    
    return data

    
def gen_q_response(info_cache, session_id, role):
    response = requests.post(url, headers=headers, json = gen_q_model(info_cache, session_id, role))
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f'response.status_code, response.text'
    
    
################## Feedback Model ################## 
def feedback_model(interview_question, final_response, info_cache, session_id, role, temperature, max_token):
    position = info_cache[session_id]['position']
    interest = info_cache[session_id]['interest']
    history = info_cache[session_id]['history']
    language = info_cache[session_id]['language']
    project = info_cache[session_id]['project']
    resume = info_cache[session_id]['resume']

    system_template = f'''
    당신은 개발 및 AI 분야의 면접을 대비하는 지원자의 응답에 피드백을 제공하는 역할을 합니다.
    면접관의 입장이 되어, 아래 면접 질문에 대한 지원자의 응답을 평가하고, 스타일이 "{role}"인 면접관으로서 다음의 기준에 따라 피드백을 작성하세요.

    - 답변의 논리성, 구체성, 표현력, 경험과의 연관성, 개선할 부분
    - 각 항목을 간결하고 명확하게 서술 (불필요하게 장황하지 않게)
    - 마지막에 피드백의 전반적인 퀄리티 점수를 1~5 범위로 부여 (5는 완벽에 가까움)

    피드백 작성 후 아래 JSON 형식으로 출력하세요:
    {{
        "content": "[피드백 본문]",
        "quality": 3
    }}
    
    ### 면접관의 질문:
    {interview_question}
    
    ### 면접관의 질문에 대한 지원자 답변:
    {final_response}
    
    ### 사용자 정보:
    - 희망 직무: {position}
    - 현재 관심사: {interest}
    - 경력: {history}
    - 주로 사용하거나 사용할 수 있는 언어: {language}
    - 프로젝트 경험: {project}
    - 이력서 정보: {resume}
    '''
    
    data = {
    "model": "sonar",
    "messages": [
        {'role': 'system', 'content': system_template},
        {"role": "user", "content": '피드백을 제공해줘'}
    ],
    "temperature": temperature,
    'max_tokens':  max_token
    }   
    
    return data
    
def feedback_response(interview_question, final_response, info_cache, session_id, role, temperature, max_token):
    payload = feedback_model(interview_question, final_response, info_cache, session_id, role, temperature, max_token)
    try:
        response = requests.post(url, headers=headers, json=payload)
    except Exception as e:
        return f"API 요청 실패: {e}", None

    if response.status_code == 200:
        try:
            result = response.json()
            message = result["choices"][0]["message"]["content"].strip()

            # ✅ JSON 형식으로 응답했는지 확인
            parsed = json.loads(message)
            feedback = parsed.get("content", "").strip()
            quality = parsed.get("quality", None)

            return feedback, quality
        except (json.JSONDecodeError, KeyError):
            # 응답이 JSON이 아니거나 파싱 실패 시 fallback
            return message, None
    else:
        return f"{response.status_code}: {response.text}", None

################## Report Model ################## 
def report_model(cache, info_cache, user_id, session_id, info_id, role, max_token, temperature):
    position = info_cache[session_id]['position']
    interest = info_cache[session_id]['interest']
    history = info_cache[session_id]['history']
    language = info_cache[session_id]['language']
    project = info_cache[session_id]['project']
    resume = info_cache[session_id]['resume']
    
    interview_content = ""
    for idx, item in enumerate(cache, start=1):
        interview_content += f"{idx}. 질문: {item['interview_question']}\n"
        interview_content += f"   답변: {item['user_response']}\n"
        interview_content += f"   피드백: {item['feedback']}\n\n"

    system_template = f'''
    당신은 개발 및 AI 분야의 면접을 대비하는 지원자의 궁금증과 답변, 피드백을 바탕으로 종합 레포트를 생성하는 면접 평가관입니다.
    면접관의 면접 스타일은 {role}입니다. 
    지원자의 정보를 고려하여 맞춤형 레포트를 제공합니다.
    아래는 사용자의 10개의 면접 문항, 답변, 피드백입니다. 이를 바탕으로 종합적인 보고서를 작성해 주세요.
    
    ### Report format
    1. 언어적 표현 특징
    2. 취약 부분
    3. 개선해야 할 점
    4. 답변의 종합적인 퀄리티로 보는 면접 대비 정도 추이
    
    ### 면접 내용:
    {interview_content}
    
    ### 사용자 정보:
    - 희망 직무: {position}
    - 현재 관심사: {interest}
    - 경력: {history}
    - 주로 사용하거나 사용할 수 있는 언어: {language}
    - 프로젝트 경험: {project}
    - 이력서 정보: {resume}
    '''
    
    data = {
    "model": "sonar",
    "messages": [
        {'role': 'system', 'content': system_template},
        {"role": "user", "content": '종합 레포트를 제공해줘'}
    ],
    "temperature": temperature,
    'max_tokens':  max_token
    }   
    
    return data

def report_response(cache, info_cache, user_id, session_id, info_id, role, max_token, temperature):
    response = requests.post(url, headers=headers, json = report_model(cache, info_cache, user_id, session_id, info_id, role, max_token, temperature))
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"{response.status_code}, {response.text}"