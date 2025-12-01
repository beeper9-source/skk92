import json
import os
from supabase import create_client, Client

# Supabase 설정 (환경 변수에서 가져오거나 직접 입력)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'YOUR_SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'YOUR_SUPABASE_ANON_KEY')

def upload_to_supabase():
    """분석 결과를 Supabase에 업로드"""
    
    # Supabase 클라이언트 생성
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # JSON 파일 로드
    with open('analysis_result.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("Supabase에 데이터 업로드 시작...")
    
    # 1. 전체 통계 업로드
    overall_stats = {
        'total_messages': data['summary']['total_messages'],
        'total_people': data['summary']['total_people'],
        'date_start': data['summary']['date_range']['start'],
        'date_end': data['summary']['date_range']['end']
    }
    
    # 기존 통계 삭제 후 새로 삽입
    supabase.table('overall_stats').delete().neq('id', 0).execute()
    supabase.table('overall_stats').insert(overall_stats).execute()
    print("✓ 전체 통계 업로드 완료")
    
    # 2. 참여자별 데이터 업로드
    for person in data['people']:
        # 참여자 정보
        participant_data = {
            'name': person['name'],
            'total_messages': person['total_messages'],
            'total_words': person['total_words'],
            'avg_message_length': person['avg_message_length'],
            'predicted_job': person['predicted_job'],
            'job_confidence': person['job_confidence'],
            'emotion_positive': person['emotions']['positive'],
            'emotion_neutral': person['emotions']['neutral'],
            'emotion_negative': person['emotions']['negative']
        }
        
        # 참여자 업데이트 또는 삽입
        existing = supabase.table('participants').select('id').eq('name', person['name']).execute()
        
        if existing.data:
            participant_id = existing.data[0]['id']
            supabase.table('participants').update(participant_data).eq('id', participant_id).execute()
        else:
            result = supabase.table('participants').insert(participant_data).execute()
            participant_id = result.data[0]['id']
        
        # 월별 통계 삭제 후 재삽입
        supabase.table('monthly_stats').delete().eq('participant_id', participant_id).execute()
        for monthly in person['monthly_trend']:
            supabase.table('monthly_stats').insert({
                'participant_id': participant_id,
                'month': monthly['month'],
                'message_count': monthly['count']
            }).execute()
        
        # 키워드 삭제 후 재삽입
        supabase.table('keywords').delete().eq('participant_id', participant_id).execute()
        for keyword in person['top_keywords']:
            supabase.table('keywords').insert({
                'participant_id': participant_id,
                'keyword': keyword['word'],
                'count': keyword['count']
            }).execute()
        
        # 직업 점수 삭제 후 재삽입
        supabase.table('job_scores').delete().eq('participant_id', participant_id).execute()
        for job, score in person['job_scores'].items():
            supabase.table('job_scores').insert({
                'participant_id': participant_id,
                'job_category': job,
                'score': score
            }).execute()
        
        print(f"✓ {person['name']} 데이터 업로드 완료")
    
    print("\n모든 데이터 업로드 완료!")

if __name__ == '__main__':
    if SUPABASE_URL == 'YOUR_SUPABASE_URL' or SUPABASE_KEY == 'YOUR_SUPABASE_ANON_KEY':
        print("⚠️  Supabase 설정이 필요합니다.")
        print("환경 변수 SUPABASE_URL과 SUPABASE_KEY를 설정하거나")
        print("코드에서 직접 값을 입력해주세요.")
    else:
        upload_to_supabase()

