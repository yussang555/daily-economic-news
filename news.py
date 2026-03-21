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
    """네이버 경제 뉴스 제목과 본문 링크를 정확히 매칭합니다."""
    # 모바일 주소가 아닌 PC용 주소를 사용해야 링크가 정확합니다.
    url = "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 헤드라인 뉴스 영역 추출
        news_list = soup.select('.sh_head_title') # 헤드라인 제목들
        if not news_list:
            news_list = soup.select('.cluster_text_headline') # 일반 뉴스 제목들

        news_results = []
        for idx, item in enumerate(news_list[:5], 1):
            title = item.get_text().strip()
            link = item.get('href')
            
            # 제목과 링크가 둘 다 있을 때만 추가
            if title and link:
                news_results.append(f"{idx}. {title}\n🔗 {link}")
            
        return "\n\n".join(news_results)
    
    except Exception as e:
        return f"뉴스 수집 중 오류 발생: {e}"

def send_telegram(text):
    """한국 시간 기준 전송 및 날짜 표기"""
    # 서버 UTC 시간을 한국 시간(KST)으로 변환
    kst_now = datetime.utcnow() + timedelta(hours=9)
    today_str = kst_now.strftime("%Y년 %m월 %d일")
    
    message = f"📢 {today_str} 아침 경제 브리핑\n\n{text}"
    
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False # 미리보기 활성화
    }
    
    response = requests.post(send_url, json=payload)
    return response.status_code == 200

if __name__ == "__main__":
    news_content = get_news()
    if send_telegram(news_content):
        print("✅ 시스템 정상 가동 중")
    else:
        print("❌ 전송 실패")