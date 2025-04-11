from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
from datetime import datetime
import os

app = Flask(__name__)

# 전역 변수로 차트 데이터 저장
chart_data = []

def crawl_melon_chart():
    global chart_data
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        url = 'https://www.melon.com/chart/index.htm'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        songs = []
        for tr in soup.select('table > tbody > tr'):
            try:
                rank = tr.select_one('.rank').text.strip()
                title = tr.select_one('.rank01 > span > a').text.strip()
                artist = tr.select_one('.rank02 > a').text.strip()
                songs.append({
                    'rank': rank,
                    'title': title,
                    'artist': artist
                })
            except:
                continue
        
        if songs:  # 크롤링이 성공적으로 이루어진 경우에만 데이터 업데이트
            chart_data = songs
            print(f"Chart updated at {datetime.now()}")
    except Exception as e:
        print(f"Error crawling chart: {e}")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html', chart_data=chart_data, datetime=datetime)

if __name__ == '__main__':
    # 초기 크롤링 실행
    crawl_melon_chart()
    
    # 1분마다 크롤링 실행
    schedule.every(1).minutes.do(crawl_melon_chart)
    
    # 스케줄러를 별도 스레드에서 실행
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Flask 서버 실행
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 