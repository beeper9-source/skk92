-- Supabase 데이터베이스 스키마 설정

-- 1. 참여자 테이블
CREATE TABLE IF NOT EXISTS participants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    total_messages INTEGER DEFAULT 0,
    total_words INTEGER DEFAULT 0,
    avg_message_length NUMERIC(10, 2) DEFAULT 0,
    predicted_job VARCHAR(100),
    job_confidence NUMERIC(5, 2) DEFAULT 0,
    predicted_age INTEGER,
    age_range VARCHAR(20),
    emotion_positive INTEGER DEFAULT 0,
    emotion_neutral INTEGER DEFAULT 0,
    emotion_negative INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. 월별 통계 테이블
CREATE TABLE IF NOT EXISTS monthly_stats (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER REFERENCES participants(id) ON DELETE CASCADE,
    month VARCHAR(7) NOT NULL, -- YYYY-MM 형식
    message_count INTEGER DEFAULT 0,
    UNIQUE(participant_id, month)
);

-- 3. 키워드 테이블
CREATE TABLE IF NOT EXISTS keywords (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER REFERENCES participants(id) ON DELETE CASCADE,
    keyword VARCHAR(100) NOT NULL,
    count INTEGER DEFAULT 0,
    UNIQUE(participant_id, keyword)
);

-- 4. 직업 점수 테이블
CREATE TABLE IF NOT EXISTS job_scores (
    id SERIAL PRIMARY KEY,
    participant_id INTEGER REFERENCES participants(id) ON DELETE CASCADE,
    job_category VARCHAR(100) NOT NULL,
    score INTEGER DEFAULT 0,
    UNIQUE(participant_id, job_category)
);

-- 5. 전체 통계 테이블
CREATE TABLE IF NOT EXISTS overall_stats (
    id SERIAL PRIMARY KEY,
    total_messages INTEGER DEFAULT 0,
    total_people INTEGER DEFAULT 0,
    date_start DATE,
    date_end DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_monthly_stats_month ON monthly_stats(month);
CREATE INDEX IF NOT EXISTS idx_keywords_participant ON keywords(participant_id);
CREATE INDEX IF NOT EXISTS idx_job_scores_participant ON job_scores(participant_id);

-- 업데이트 시간 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
DROP TRIGGER IF EXISTS update_participants_updated_at ON participants;
CREATE TRIGGER update_participants_updated_at
    BEFORE UPDATE ON participants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

