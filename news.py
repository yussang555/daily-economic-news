import os
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ==========================================
# 1. 환경 설정 및 키워드 지정 (대장님 맞춤형)
# ==========================================
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 받고 싶은 키워드를 이 리스트에 넣으세요. 
# 영문은 대소문자 구분 없이 작동하도록 설계했습니다.
KEYWORDS = ["나스닥", "S&P500", "미국채", "금리", "부동산", "국채", "전쟁", "환율", "유가", "AI", "코스피", "반도체", "연준"]
# ==========================================

def get_news():
    """뉴스 목록을 긁어와서 키워드와 매칭되는 것만 골라냅니다."""
    url = "https://finance.naver.com/news/news_list.naver?mode=RANK"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 랭킹 뉴스 목록 수집 (범위를 더 넓혀서 20개 중 키워드를 찾습니다)
        news_items = soup.select('.simpleNewsList li')
        
        filtered_news = []
        count = 1
        
        for item in news_items[:20]: # 더 많은 뉴스 중에서 키워드를 검색합니다.
            a_tag = item.select_one('a')
            if a_tag:
                title = a_tag.text.strip()
                
                # 키워드 매칭 검사 (하나라도 포함되면 수집)
                if any(kw.lower() in title.lower() for kw in KEYWORDS):
                    link = a_tag['href']
                    
                    # 다이렉트 링크 생성 (지난번 성공한 로직 그대로 유지)
                    office_id = re.search(r'office_id=(\d+)', link)
                    article_id = re.search(r'article_id=(\d+)', link)
                    
                    if office_id and article_id:
                        direct_link = f"https://n.news.naver.com/mnews/article/{office_id.group(1)}/{article_id.group(1)}"
                        filtered_news.append(f"{count}. {title}\n🔗 {direct_link}")
                        count += 1
            
        return "\n\n".join(filtered_news)
    
    except Exception as e:
        return f"뉴스 수집 중 오류 발생: {e}"

def send_telegram(text):
    """결과가 있을 때만 텔레그램 전송"""
    # 키워드에 맞는 뉴스가 없으면 전송하지 않음 (대장님의 휴식 보장)
    if not text:
        print("매칭되는 키워드 뉴스가 없습니다.")
        return False

    kst_now = datetime.utcnow() + timedelta(hours=9)
    today_str = kst_now.strftime("%Y년 %m월 %d일")
    
    message = f"🎯 {today_str} 대장님 맞춤 경제 브리핑\n\n[설정 키워드: {', '.join(KEYWORDS)}]\n\n{text}"
    
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }
    
    response = requests.post(send_url, json=payload)
    return response.status_code == 200

if __name__ == "__main__":
    content = get_news()
    send_telegram(content)