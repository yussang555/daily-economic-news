import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ==========================================
# GitHub Secrets에서 정보를 가져오도록 수정
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# ==========================================

def get_news():
    url = "https://finance.naver.com/news/mainnews.naver"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('.articleSubject a')[:5]
        
        news_data = []
        for idx, article in enumerate(articles, 1):
            title = article.text.strip()
            link = "https://finance.naver.com" + article['href']
            news_data.append(f"{idx}. {title}\n🔗 {link}")
        return "\n\n".join(news_data)
    except Exception as e:
        return f"뉴스 수집 중 오류: {e}"

def send_telegram(text):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    message = f"📢 {today} 아침 경제 브리핑\n\n{text}"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    return response.status_code == 200

if __name__ == "__main__":
    content = get_news()
    if send_telegram(content):
        print("✅ 텔레그램으로 뉴스를 보냈습니다!")
    else:
        print("❌ 전송 실패. 토큰/ID를 확인하세요.")