# 대학동기 대화 분석 시스템

카카오톡 대화 내보내기 파일을 분석하여 대학동기들의 대화 양, 성향, 예상 직업 등을 분석하는 시스템입니다.

## 기능

- 📊 개인별 대화량 분석
- 📈 월별 대화량 추이 시각화
- 💼 대화 내용 기반 예상 직업 추론
- 😊 감정 분석 (긍정/중립/부정)
- 🔍 주요 키워드 추출
- 💾 Supabase 데이터베이스 연동

## 설치 및 사용 방법

### 1. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 대화 파일 분석

```bash
python parse_chat.py
```

이 명령어를 실행하면 `analysis_result.json` 파일이 생성됩니다.

### 3. 웹 대시보드 확인

`index.html` 파일을 웹 브라우저에서 열어 시각화된 결과를 확인할 수 있습니다.

### 4. Supabase 연동 (선택사항)

1. Supabase 프로젝트 생성
2. `supabase_setup.sql` 파일을 실행하여 테이블 생성
3. 환경 변수 설정:
   ```bash
   export SUPABASE_URL="your_supabase_url"
   export SUPABASE_KEY="your_supabase_anon_key"
   ```
4. 데이터 업로드:
   ```bash
   python upload_to_supabase.py
   ```

## 파일 구조

- `Talk.txt`: 카카오톡 대화 내보내기 파일
- `parse_chat.py`: 대화 파일 파싱 및 분석 스크립트
- `analysis_result.json`: 분석 결과 JSON 파일
- `index.html`: 시각화 대시보드
- `supabase_setup.sql`: Supabase 데이터베이스 스키마
- `upload_to_supabase.py`: Supabase 데이터 업로드 스크립트

## 분석 항목

### 개인별 분석
- 총 메시지 수
- 총 단어 수
- 평균 메시지 길이
- 월별 메시지 추이
- 주요 키워드 (상위 10개)
- 감정 분포 (긍정/중립/부정)
- 예상 직업 및 신뢰도

### 전체 분석
- 총 메시지 수
- 참여자 수
- 분석 기간
- 월별 전체 대화량
- 직업 분포

## 예상 직업 카테고리

- 개발자/IT
- 마케팅/광고
- 디자인
- 경영/사업
- 교육
- 의료
- 법률
- 공공기관/공무원
- 언론/미디어
- 연구/분석

## 주의사항

- 대화 파일은 UTF-8 인코딩이어야 합니다.
- 카카오톡 대화 내보내기 형식이 변경되면 파싱 로직을 수정해야 할 수 있습니다.
- 예상 직업은 대화 내용의 키워드를 기반으로 추론하므로 정확도가 100%는 아닙니다.

