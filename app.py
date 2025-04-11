from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import schedule
import time
import threading
from datetime import datetime
import os
import json

app = Flask(__name__)

# 전역 변수로 차트 데이터 저장
chart_data = []
last_successful_data = []  # 마지막으로 성공한 크롤링 데이터 저장

def crawl_melon_chart():
    global chart_data, last_successful_data
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://www.melon.com/chart/index.htm',
        'Cookie': 'PCID=16779335188081870956454'
    }
    
    try:
        # 멜론 차트 API 호출
        url = 'https://www.melon.com/chart/index.json'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                # API 응답이 실패하면 웹 페이지에서 크롤링 시도
                chart_page_url = 'https://www.melon.com/chart/index.htm'
                response = requests.get(chart_page_url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                songs = []
                song_elements = soup.select('#frm table tbody tr')
                
                for element in song_elements:
                    try:
                        rank = element.select_one('.rank').text.strip()
                        title_element = element.select_one('.wrap_song_info .rank01 span a')
                        artist_element = element.select_one('.wrap_song_info .rank02 span a')
                        
                        if title_element and artist_element:
                            title = title_element.text.strip()
                            artist = artist_element.text.strip()
                            
                            songs.append({
                                'rank': rank,
                                'title': title,
                                'artist': artist
                            })
                    except Exception as e:
                        print(f"Error parsing song element: {e}")
                        continue
                
                if len(songs) > 0:
                    chart_data = songs
                    last_successful_data = songs
                    print(f"Chart updated successfully at {datetime.now()} with {len(songs)} songs")
                    
                    # 성공한 데이터를 파일에 저장
                    try:
                        with open('last_chart_data.json', 'w', encoding='utf-8') as f:
                            json.dump(songs, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        print(f"Error saving backup data: {e}")
                else:
                    print("No songs found in the response")
                    if last_successful_data:
                        chart_data = last_successful_data
            except Exception as e:
                print(f"Error parsing webpage: {e}")
                if last_successful_data:
                    chart_data = last_successful_data
        else:
            print(f"Error: Status code {response.status_code}")
            if last_successful_data:
                chart_data = last_successful_data
                
    except Exception as e:
        print(f"Error crawling chart: {e}")
        if last_successful_data:
            chart_data = last_successful_data
        else:
            # 백업 파일에서 데이터 로드 시도
            try:
                with open('last_chart_data.json', 'r', encoding='utf-8') as f:
                    chart_data = json.load(f)
                    print("Loaded backup data from file")
            except Exception as e:
                print(f"Error loading backup data: {e}")

def run_scheduler():
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            print(f"Scheduler error: {e}")
            time.sleep(1)

@app.route('/')
def index():
    global chart_data
    if not chart_data and os.path.exists('last_chart_data.json'):
        try:
            with open('last_chart_data.json', 'r', encoding='utf-8') as f:
                chart_data = json.load(f)
        except Exception as e:
            print(f"Error loading backup data: {e}")
    
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