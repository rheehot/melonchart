# Melon Chart Viewer

실시간 멜론 차트 TOP 100을 보여주는 웹 애플리케이션입니다.

## 특징

- 멜론 TOP 100 차트 실시간 표시
- 1분마다 자동 업데이트
- 반응형 디자인

## 기술 스택

- Python 3.9
- Flask
- BeautifulSoup4
- Schedule
- Bootstrap 5

## 로컬에서 실행하기

1. 저장소 클론
```bash
git clone [repository-url]
cd melon-chart
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 애플리케이션 실행
```bash
python app.py
```

5. 웹 브라우저에서 http://localhost:5000 접속

## 배포

이 프로젝트는 Render에서 호스팅됩니다. 