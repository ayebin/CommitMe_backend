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

def summarize_resume(text):    
    prompt = f'''
    다음은 어떤 사람의 이력서입니다.

    면접 질문을 만들기 위해 필요한 핵심 정보를 요약해 주세요.  
    특히 다음 사항에 주목해서 요약해 주세요:

    1. 지원자가 했던 프로젝트나 업무 경험에서 특별하거나 독특한 점  
    2. 관심 분야 및 목표  
    3. 사용 가능한 기술 스택 또는 도구  
    4. 성장 과정에서 강조하고 싶은 부분  
    5. 기타 면접에서 질문거리로 삼을 만한 특징

    이력서:
    {text}

    면접 질문 생성을 위한 요약:
    '''
    
    payload = {
        "model": "sonar",  # 또는 sonar-medium-chat, sonar-large-chat 등
        "messages": [
            {"role": "system", "content": "당신은 이력서를 요약하는 도우미입니다."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 3000
    }


    try:
        response = requests.post(url, headers=headers, json=payload)
        print(response.status_code)
        response.raise_for_status()

        result = response.json()
        summary = result['choices'][0]['message']['content'].strip()
        return summary

    except Exception as e:
        print(f"요약 실패: {e}")
        return text  # 실패 시 원문 그대로 반환