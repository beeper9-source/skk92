import re
from collections import defaultdict
from datetime import datetime
import json

def parse_chat_file(filename):
    """카카오톡 대화 내보내기 파일을 파싱"""
    messages = []
    current_date = None
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 날짜 라인 감지 (예: "2025년 5월 31일 토요일")
        date_match = re.match(r'(\d{4})년 (\d{1,2})월 (\d{1,2})일', line)
        if date_match:
            year, month, day = date_match.groups()
            current_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            continue
        
        # 메시지 라인 파싱 (예: "2025. 5. 31. 오후 1:38, 거북코 : 사진")
        message_match = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.\s*(오전|오후)\s*(\d{1,2}):(\d{2}),\s*([^:]+)\s*:\s*(.+)', line)
        if message_match:
            year, month, day, ampm, hour, minute, name, content = message_match.groups()
            
            # 24시간 형식으로 변환
            hour = int(hour)
            if ampm == '오후' and hour != 12:
                hour += 12
            elif ampm == '오전' and hour == 12:
                hour = 0
            
            month_str = month.zfill(2)
            day_str = day.zfill(2)
            hour_str = str(hour).zfill(2)
            minute_str = minute.zfill(2)
            
            timestamp = f"{year}-{month_str}-{day_str} {hour_str}:{minute_str}:00"
            date_only = f"{year}-{month_str}-{day_str}"
            month_key = f"{year}-{month_str}"
            
            # 봇 메시지 제외
            if name.strip() in ['방장봇', '시스템']:
                continue
            
            messages.append({
                'timestamp': timestamp,
                'date': date_only,
                'month': month_key,
                'name': name.strip(),
                'content': content.strip(),
                'word_count': len(content.split()) if content.strip() not in ['사진', '이모티콘', '동영상', '파일'] else 0
            })
    
    return messages

def analyze_messages(messages):
    """메시지를 분석하여 통계 생성"""
    stats = {
        'total_messages': len(messages),
        'by_person': defaultdict(lambda: {
            'count': 0,
            'word_count': 0,
            'messages': [],
            'by_month': defaultdict(int),
            'keywords': defaultdict(int),
            'emotions': {'positive': 0, 'neutral': 0, 'negative': 0}
        }),
        'by_month': defaultdict(int),
        'by_date': defaultdict(int)
    }
    
    # 긍정/부정 키워드
    positive_keywords = ['좋', '행복', '즐거', '재미', '고마', '감사', '축하', '완벽', '멋', '이쁘', '예쁘', 'ㅎㅎ', 'ㅋㅋ', '하하']
    negative_keywords = ['슬', '힘들', '아픈', '화나', '짜증', '불편', '문제', '어려', '고생', '피곤', '스트레스']
    
    # 직업 관련 키워드
    job_keywords = {
        '개발자/IT': ['코딩', '프로그래밍', '개발', '소프트웨어', '앱', '웹', '서버', '데이터베이스', 'API', '버그', '디버깅', 'git', 'github'],
        '마케팅/광고': ['마케팅', '광고', '홍보', '브랜드', '캠페인', 'SNS', '인스타', '페이스북'],
        '디자인': ['디자인', 'UI', 'UX', '그래픽', '포토샵', '일러스트', '레이아웃', '색상'],
        '경영/사업': ['사업', '창업', '경영', '매출', '수익', '투자', '주식', '비즈니스'],
        '교육': ['학생', '교수', '강의', '교육', '수업', '과제', '시험'],
        '의료': ['병원', '의사', '간호', '진료', '처방', '수술'],
        '법률': ['법률', '변호사', '법원', '소송', '계약'],
        '공공기관': ['출장', '회의', '보고서', '기관', '정부', '공무원', '행정'],
        '언론/미디어': ['기자', '뉴스', '보도', '방송', '언론', '기사'],
        '연구': ['연구', '논문', '실험', '분석', '데이터', '통계']
    }
    
    for msg in messages:
        name = msg['name']
        content = msg['content'].lower()
        
        # 기본 통계
        stats['by_person'][name]['count'] += 1
        stats['by_person'][name]['word_count'] += msg['word_count']
        stats['by_person'][name]['messages'].append(msg)
        stats['by_person'][name]['by_month'][msg['month']] += 1
        stats['by_month'][msg['month']] += 1
        stats['by_date'][msg['date']] += 1
        
        # 키워드 추출 (2글자 이상 단어만)
        words = re.findall(r'\b\w{2,}\b', content)
        for word in words:
            if len(word) >= 2:
                stats['by_person'][name]['keywords'][word] += 1
        
        # 감정 분석
        has_positive = any(kw in content for kw in positive_keywords)
        has_negative = any(kw in content for kw in negative_keywords)
        
        if has_positive and not has_negative:
            stats['by_person'][name]['emotions']['positive'] += 1
        elif has_negative:
            stats['by_person'][name]['emotions']['negative'] += 1
        else:
            stats['by_person'][name]['emotions']['neutral'] += 1
    
    return stats

def predict_job(name, person_stats):
    """대화 내용을 기반으로 예상 직업 추론"""
    messages = person_stats['messages']
    all_content = ' '.join([msg['content'].lower() for msg in messages])
    
    job_scores = defaultdict(int)
    
    # 직업 관련 키워드 매칭
    job_keywords = {
        '개발자/IT': ['코딩', '프로그래밍', '개발', '소프트웨어', '앱', '웹', '서버', '데이터베이스', 'db', 'api', '버그', '디버깅', 'git', 'github', '코드', '프로젝트', '배포', '테스트', '프레임워크', '라이브러리'],
        '마케팅/광고': ['마케팅', '광고', '홍보', '브랜드', '캠페인', 'sns', '인스타', '페이스북', '유튜브', '콘텐츠', '인플루언서'],
        '디자인': ['디자인', 'ui', 'ux', '그래픽', '포토샵', '일러스트', '레이아웃', '색상', '브랜딩', '로고'],
        '경영/사업': ['사업', '창업', '경영', '매출', '수익', '투자', '주식', '비즈니스', '스타트업', '벤처'],
        '교육': ['학생', '교수', '강의', '교육', '수업', '과제', '시험', '학교', '대학'],
        '의료': ['병원', '의사', '간호', '진료', '처방', '수술', '환자', '약'],
        '법률': ['법률', '변호사', '법원', '소송', '계약', '법적'],
        '공공기관/공무원': ['출장', '회의', '보고서', '기관', '정부', '공무원', '행정', '부서', '과장', '부장', '회의자료', '기관방문'],
        '언론/미디어': ['기자', '뉴스', '보도', '방송', '언론', '기사', '보도자료'],
        '연구/분석': ['연구', '논문', '실험', '분석', '데이터', '통계', '리포트', '요약', 'gemini', 'chatgpt', 'ai']
    }
    
    for job, keywords in job_keywords.items():
        for keyword in keywords:
            if keyword in all_content:
                job_scores[job] += all_content.count(keyword)
    
    # 키워드 빈도 기반 점수 계산
    top_keywords = sorted(person_stats['keywords'].items(), key=lambda x: x[1], reverse=True)[:20]
    for word, count in top_keywords:
        for job, keywords in job_keywords.items():
            if word in keywords:
                job_scores[job] += count * 2  # 키워드 빈도에 가중치
    
    if job_scores:
        predicted_job = max(job_scores.items(), key=lambda x: x[1])[0]
        confidence = job_scores[predicted_job] / sum(job_scores.values()) * 100 if sum(job_scores.values()) > 0 else 0
        return predicted_job, confidence, dict(job_scores)
    
    return '미정', 0, {}

def generate_analysis_report(messages, stats):
    """분석 결과 리포트 생성"""
    report = {
        'summary': {
            'total_messages': stats['total_messages'],
            'total_people': len(stats['by_person']),
            'date_range': {
                'start': min([msg['date'] for msg in messages]) if messages else None,
                'end': max([msg['date'] for msg in messages]) if messages else None
            }
        },
        'people': []
    }
    
    for name, person_stats in stats['by_person'].items():
        # 월별 메시지 수
        monthly_data = []
        for month in sorted(person_stats['by_month'].keys()):
            monthly_data.append({
                'month': month,
                'count': person_stats['by_month'][month]
            })
        
        # 상위 키워드
        top_keywords = sorted(person_stats['keywords'].items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 예상 직업
        predicted_job, confidence, job_scores = predict_job(name, person_stats)
        
        # 대화 성향 분석
        total_emotions = sum(person_stats['emotions'].values())
        emotion_ratio = {
            'positive': person_stats['emotions']['positive'] / total_emotions * 100 if total_emotions > 0 else 0,
            'neutral': person_stats['emotions']['neutral'] / total_emotions * 100 if total_emotions > 0 else 0,
            'negative': person_stats['emotions']['negative'] / total_emotions * 100 if total_emotions > 0 else 0
        }
        
        # 평균 메시지 길이
        avg_length = person_stats['word_count'] / person_stats['count'] if person_stats['count'] > 0 else 0
        
        report['people'].append({
            'name': name,
            'total_messages': person_stats['count'],
            'total_words': person_stats['word_count'],
            'avg_message_length': round(avg_length, 2),
            'monthly_trend': monthly_data,
            'top_keywords': [{'word': k, 'count': v} for k, v in top_keywords],
            'predicted_job': predicted_job,
            'job_confidence': round(confidence, 1),
            'job_scores': job_scores,
            'emotion_ratio': emotion_ratio,
            'emotions': person_stats['emotions']
        })
    
    # 메시지 수로 정렬
    report['people'].sort(key=lambda x: x['total_messages'], reverse=True)
    
    return report

if __name__ == '__main__':
    print("카카오톡 대화 파일 파싱 중...")
    messages = parse_chat_file('Talk.txt')
    print(f"총 {len(messages)}개의 메시지를 파싱했습니다.")
    
    print("메시지 분석 중...")
    stats = analyze_messages(messages)
    print(f"총 {len(stats['by_person'])}명의 참여자를 발견했습니다.")
    
    print("리포트 생성 중...")
    report = generate_analysis_report(messages, stats)
    
    # JSON 파일로 저장
    with open('analysis_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("분석 완료! analysis_result.json 파일이 생성되었습니다.")
    
    # 간단한 통계 출력
    print("\n=== 참여자별 메시지 수 ===")
    for person in report['people']:
        print(f"{person['name']}: {person['total_messages']}개 메시지")
        print(f"  예상 직업: {person['predicted_job']} (신뢰도: {person['job_confidence']:.1f}%)")
        print(f"  평균 메시지 길이: {person['avg_message_length']:.1f}단어")
        print()

