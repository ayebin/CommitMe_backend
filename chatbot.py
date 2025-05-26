import os
import requests
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), 'api.env')
load_dotenv(dotenv_path)

API_KEY = os.getenv("PERPLEXITY_API_KEY")

url = "https://api.perplexity.ai/chat/completions"  
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def setting_model(info_cache, session_id, role, user, temperature, max_token):
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
    사용자가 '준비됨' 또는 '시작'과 같은 메시지를 주면, 면접이 시작됩니다.
    
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


def get_response(info_cache, session_id, role, user, temperature, max_token):
    response = requests.post(url, headers=headers, json = setting_model(info_cache, session_id, role, user, temperature, max_token))
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f'response.status_code, response.text'
