import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ==========================================
# GitHub Secrets 설정
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# ==========================================

def get_news():
    """가장 안정적인 네이버 금융 뉴스 페이지를 수집합니다."""
    # 구조가 비교적 고정된 '많이 본 뉴스' 페이지 활용
    url = "https://finance.naver.com/news/news_list.naver?mode=RANK"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 뉴스 항목들 찾기
        news_items = soup.select('.simpleNewsList li')
        
        if not news_items:
            return "뉴스를 수집하지 못했습니다. 페이지 구조를 확인해주세요."

        news_results = []
        for idx, item in enumerate(news_items[:5], 1):
            a_tag = item.select_one('a')
            if a_tag:
                title = a_tag.text.strip()
                link = "https://finance.naver.com" + a_tag['href']
                news_results.append(f"{idx}. {title}\n🔗 {link}")
            
        return "\n\n".join(news_results)
    
    except Exception as e:
        return f"뉴스 수집 중 오류 발생: {e}"

def send_telegram(text):
    """한국 시간 기준 전송"""
    kst_now = datetime.utcnow() + timedelta(hours=9)
    today_str = kst_now.strftime("%Y년 %m월 %d일")
    
    # 텍스트가 비어있으면 전송 안 함
    if not text or "수집하지 못했습니다" in text:
        message = f"📢 {today_str} 알림\n\n현재 뉴스 수집에 문제가 발생했습니다."
    else:
        message = f"📢 {today_str} 아침 경제 브리핑\n\n{text}"
    
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