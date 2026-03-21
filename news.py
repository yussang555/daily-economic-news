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
    """기사 본문으로 직접 연결되는 확실한 링크를 수집합니다."""
    # 모바일용이 아닌 PC용 메인 뉴스 페이지를 긁어야 링크가 정확합니다.
    url = "https://finance.naver.com/news/mainnews.naver"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 기사 제목과 링크가 포함된 영역 선택
        articles = soup.select('.mainNewsList .block1')[:5]
        
        if not articles:
            articles = soup.select('.articleSubject')[:5]

        news_data = []
        for idx, item in enumerate(articles, 1):
            link_tag = item.select_one('a')
            if link_tag:
                title = link_tag.text.strip()
                link = link_tag['href']
                
                # 링크 정제: 본문으로 바로 가는 주소 체계로 강제 변환
                if link.startswith('/news/'):
                    link = "https://finance.naver.com" + link
                
                # 가끔 링크에 불필요한 파라미터가 붙어 목록으로 튕기는 것 방지
                # 텔레그램 메시지 생성
                news_data.append(f"{idx}. {title}\n🔗 {link}")
            
        return "\n\n".join(news_data)
    
    except Exception as e:
        return f"뉴스 수집 중 오류 발생: {e}"

def send_telegram(text):
    """한국 시간 기준 전송 및 날짜 수정"""
    # 서버 UTC 시간을 한국 시간(KST)으로 변환
    kst_now = datetime.utcnow() + timedelta(hours=9)
    today_str = kst_now.strftime("%Y년 %m월 %d일")
    
    message = f"📢 {today_str} 아침 경제 브리핑\n\n{text}"
    
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False  # 미리보기 활성화하여 신뢰도 향상
    }
    
    response = requests.post(send_url, json=payload)
    return response.status_code == 200

if __name__ == "__main__":
    news_content = get_news()
    if send_telegram(news_content):
        print("✅ 기사 본문 다이렉트 링크 전송 성공!")
    else:
        print("❌ 전송 실패")