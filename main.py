import os
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
import google.generativeai as genai

# 금고(Secrets)에서 API 키 불러오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")

genai.configure(api_key=GEMINI_API_KEY)
# 🚨 요금제 제한(429 에러)을 피하기 위해 반드시 완전 무료인 Flash 모델 사용
model = genai.GenerativeModel('gemini-3.5-flash')

def get_naver_news(query, display=10):
    encText = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/news?query={encText}&display={display}&sort=sim"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)
    try:
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            return json.loads(response.read().decode('utf-8'))['items']
    except Exception as e:
        print(f"네이버 뉴스 검색 실패: {e}")
    return []

def main():
    today_str = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y년 %m월 %d일")

    # 뉴스 수집량 넉넉하게 확보
    bio_news = get_naver_news("제약 바이오 품질관리 QA QC", 5)
    econ_news = get_naver_news("글로벌 경제 거시경제 동향", 10)

    prompt = f"""
    너는 제약·바이오 QA/QC 취업 전문 컨설턴트야. 아래 데이터를 분석해 JSON을 생성해.

    [바이오 뉴스]: {bio_news}
    [경제 뉴스]: {econ_news}

    [필수 반영 조건]
    1. news.one_line_summary: "대웅제약은 송도에 신규 GMP 제조소를 구축하고 QA/QC 등 핵심 인력을 채용하여, 미래 주력 사업인 첨단바이오의약품(세포치료제·엑소좀 등) 시장 주도권 확보를 추진함." 이 예시와 완벽히 동일한 분량과 문체로, 취준생에게 필요한 최신 동향 중심의 한 줄 요약을 무조건 작성할 것.
    2. jobs: 가상의 '4년제 학사 신입' 제약/바이오 QA/QC 공고를 무조건 3개 이상 생성할 것. (대기업 1개, 중소/중견기업 2~3개. 강소기업 단어 절대 금지). link는 임시로 "#"을 넣을 것.
    3. economy: 당일 네이버 경제 뉴스 헤드라인 중 가장 중요한 이슈를 무조건 3개 이상 선별해 요약할 것.

    [출력 JSON 양식] (반드시 아래 구조를 지키고, jobs와 economy 배열에는 객체가 3개 이상 들어가야 함)
    {{
        "date": "{today_str}",
        "news": {{
            "headline": "...",
            "summary": "...",
            "one_line_summary": "...",
            "link": "...",
            "qa_insight": "...",
            "qc_insight": "..."
        }},
        "strategy": {{
            "title": "...",
            "points": ["...", "..."]
        }},
        "jobs": [
            {{
                "company": "기업명",
                "type": "대기업, 중견기업, 중소기업 중 택1",
                "title": "공고명",
                "location": "근무지",
                "education": "학사 이상",
                "deadline": "2026.07.xx",
                "analysis": "해당 직무 인재상 및 역량 분석",
                "link": "#"
            }},
            {{
                "company": "두 번째 기업명",
                "type": "중소기업",
                "title": "공고명",
                "location": "근무지",
                "education": "학사 이상",
                "deadline": "2026.07.xx",
                "analysis": "...",
                "link": "#"
            }},
            {{
                "company": "세 번째 기업명",
                "type": "중소기업",
                "title": "공고명",
                "location": "근무지",
                "education": "학사 이상",
                "deadline": "2026.07.xx",
                "analysis": "...",
                "link": "#"
            }}
        ],
        "economy": [
            {{ "headline": "...", "summary": "..." }},
            {{ "headline": "...", "summary": "..." }},
            {{ "headline": "...", "summary": "..." }}
        ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:-3].strip()
            
        json_data = json.loads(result_text)

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        print("성공적으로 data.json 파일이 생성되었습니다.")
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        raise e # 에러 발생 시 조용히 넘어가지 않고 시스템에 보고하도록 강제 설정

if __name__ == "__main__":
    main()
