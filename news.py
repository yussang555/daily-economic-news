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
    """기사 번호만 추출해서 본문으로 바로 꽂히는 링크를 만듭니다."""
    url = "https://finance.naver.com/news/news_list.naver?mode=RANK"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = soup.select('.simpleNewsList li')
        
        news_results = []
        for idx, item in enumerate(news_items[:5], 1):
            a_tag = item.select_one('a')
            if a_tag:
                title = a_tag.text.strip()
                link = a_tag['href']
                
                # 링크에서 기사 번호와 언론사 번호만 추출해서 재조립 (목록 튕김 방지)
                # 예: /news/news_read.naver?article_id=000123&office_id=011...
                final_link = "https://n.news.naver.com/mnews/article/"
                
                import re
                office_id = re.search(r'office_id=(\d+)', link)
                article_id = re.search(r'article_id=(\d+)', link)
                
                if office_id and article_id:
                    # 네이버 모바일 통합 뉴스 주소로 변환
                    direct_link = f"{final_link}{office_id.group(1)}/{article_id.group(1)}"
                    news_results.append(f"{idx}. {title}\n🔗 {direct_link}")
                else:
                    # 추출 실패 시 기본 링크라도 제공
                    news_results.append(f"{idx}. {title}\n🔗 https://finance.naver.com{link}")
            
        return "\n\n".join(news_results)
    
    except Exception as e:
        return f"뉴스 수집 중 오류 발생: {e}"

def send_telegram(text):
    """한국 시간 기준 전송"""
    kst_now = datetime.utcnow() + timedelta(hours=9)
    today_str = kst_now.strftime("%Y년 %m월 %d일")
    
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