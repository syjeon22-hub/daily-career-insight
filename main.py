```python
import os
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
import google.generativeai as genai

# 1. 금고(Secrets)에 저장해둔 API 키 불러오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

# 제미나이 AI 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_naver_news(query, display=5):
    """네이버 API를 사용해 뉴스를 검색합니다."""
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/news?query={encText}&display={display}&sort=sim"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
    
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if rescode == 200:
            response_body = response.read()
            return json.loads(response_body.decode('utf-8'))['items']
        else:
            return []
    except Exception as e:
        print(f"네이버 뉴스 검색 실패: {e}")
        return []

def main():
    # 2. 오늘 날짜 생성 (한국 시간 기준)
    today_str = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y년 %m월 %d일")

    # 3. 데이터 수집
    bio_news = get_naver_news("제약 바이오 품질관리 QA QC", 3)
    econ_news = get_naver_news("글로벌 경제 산업 동향", 3)

    # 4. 제미나이(Gemini)에게 데이터 분석 및 JSON 생성 요청
    prompt = f"""
    너는 제약·바이오 QA/QC 취업 전문 컨설턴트야.
    아래 제공된 뉴스 데이터를 분석해서, 반드시 아래의 JSON 포맷에 맞춰서 답변을 생성해줘. 다른 말은 절대 하지 말고 JSON만 출력해.

    [수집된 바이오 뉴스]: {bio_news}
    [수집된 경제 뉴스]: {econ_news}

    [출력해야 할 JSON 양식]
    {{
        "date": "{today_str}",
        "news": {{
            "headline": "바이오 뉴스 중 가장 중요한 1개 제목",
            "summary": "해당 뉴스의 핵심 내용 요약 (2문장)",
            "link": "해당 뉴스의 원문 링크",
            "qa_insight": "이 뉴스가 QA(품질보증) 직무 지원자에게 시사하는 점 (GMP, SOP 등 전문용어 포함)",
            "qc_insight": "이 뉴스가 QC(품질관리) 직무 지원자에게 시사하는 점 (기기분석, 데이터 무결성 등 전문용어 포함)"
        }},
        "strategy": {{
            "title": "오늘의 뉴스 기반 취업 전략 한 줄 요약",
            "points": ["구체적인 실행 전략 1", "구체적인 실행 전략 2", "구체적인 실행 전략 3"]
        }},
        "jobs": [
            {{
                "company": "가상의 제약사 이름 또는 뉴스에 언급된 기업",
                "title": "QA/QC 신입 채용",
                "link": "#",
                "analysis": "해당 직무 인재상 및 필수 역량 분석"
            }}
        ],
        "economy": [
            {{
                "headline": "경제 뉴스 1 제목",
                "summary": "경제 뉴스 1 요약 (거시적 관점)"
            }},
            {{
                "headline": "경제 뉴스 2 제목",
                "summary": "경제 뉴스 2 요약 (거시적 관점)"
            }}
        ]
    }}
    """

    try:
        # AI 결과물 받기
        response = model.generate_content(prompt)
        # 마크다운 블록(```json ... ```) 제거 후 순수 텍스트만 추출
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:-3].strip()
            
        json_data = json.loads(result_text)

        # 5. data.json 파일로 저장
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        print("성공적으로 data.json 파일이 생성되었습니다.")

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
```
