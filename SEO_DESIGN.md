# SEO 블로그 최적화 시스템 설계

## 요구사항

### 1. SEO 설정 항목 (글별로 다름)

각 글마다 다음 8가지 SEO 기준을 다르게 설정:

1. **통 키워드 출현 횟수** (예: 5번)
2. **조각 키워드 출현 횟수** (예: 강남 10번, 맛집 4번)
3. **글자수** (예: 1000자)
4. **금칙어 치환 여부** (O/X)
5. **첫 문단 통 키워드 2회 반복** (O/X)
6. **첫 문단 통 키워드 사이 2문장 이상 삽입** (O/X)
7. **서브 키워드 목록 수** (예: 20개 - 2번 이상 등장하는 단어)
8. **통 키워드로 시작하는 문장 수** (예: 6개)

### 2. 키워드 용어 정의

#### 통 키워드 (핵심 키워드)
- 전체 키워드 문구
- 예: "강남 맛집 추천"

#### 조각 키워드
- 통 키워드가 띄어쓰기 포함 2단어 이상일 경우 각 단어
- 예: "강남", "맛집", "추천"
- 통 키워드가 단일 단어면 조각 키워드 없음

#### 서브 키워드
- 통/조각 키워드 제외
- 원고에 2번 이상 등장하는 단어
- 중복 문장부호도 카운트 (^^, ??, ..., ;;)
- ?? 와 ??? 는 다른 서브 키워드
- **개수만 세면 됨** (몇 개의 서브 키워드가 있는지)

### 3. 키워드 카운팅 규칙

#### 띄어쓰기 기준 카운팅

✅ **카운트 됨:**
```
"강남 맛집 추천 리스트 파악을 위해"
→ 통 키워드 1회 (뒤에 띄어쓰기 있음)
```

❌ **카운트 안 됨:**
```
"강남 맛집 추천을 받기 위해"
→ 통 키워드 0회 (조사 '을' 바로 붙음)
→ 조각 키워드: '강남' 1회, '맛집' 1회만 카운트
```

#### 한글자 조사 처리

**문제:** 한글자 조사는 띄어쓰기하면 부자연스러움
- 한글자 조사: 를/을/가/이/는/은/에/의

**해결:** 우회 문장으로 수정
```
Before: "강남 맛집 추천을 받기 위해"
After:  "강남 맛집 추천 리스트 확보를 위해"
→ 통 키워드 카운트 가능하게!
```

#### 두글자 이상 조사

**허용:** 띄어쓰기 OK (덜 부자연스러움)
```
Before: "강남 맛집 추천으로 리꼬르라는"
After:  "강남 맛집 추천 으로 리꼬르라는"
→ 통 키워드 카운트 가능!
```

### 4. 글 구조 요구사항

#### 템플릿 플로우
1. **도입부:** 불편함/궁금한 것/고민 소개
2. **중간:** 핵심 키워드를 물어보기
3. **마지막:** 댓글로 정보 공유 요청

#### 중요한 점
- 글은 순수 질문/고민 형태 (제품 홍보 NO)
- 댓글에서 제품 홍보를 함
- 원고 초반부/마지막에 "댓글로 정보 공유해달라" 문장 필요

## 시스템 설계

### 클래스 구조

#### 1. SEOConfig (SEO 설정)
```python
@dataclass
class SEOConfig:
    # 통 키워드 설정
    whole_keyword: str                    # 통 키워드 (예: "강남 맛집 추천")
    whole_keyword_count: int              # 출현 횟수 (예: 5)

    # 조각 키워드 설정
    piece_keywords: Dict[str, int]        # {단어: 출현횟수} (예: {"강남": 10, "맛집": 4})

    # 글 설정
    char_count: int                       # 글자수 (예: 1000)
    apply_forbidden_words: bool           # 금칙어 치환 (O/X)

    # 첫 문단 설정
    first_para_keyword_twice: bool        # 첫 문단 통키워드 2회 (O/X)
    first_para_two_sentences_between: bool # 키워드 사이 2문장 이상 (O/X)

    # 서브 키워드 설정
    sub_keyword_count: int                # 서브 키워드 목록 수 (예: 20)

    # 문장 구조
    sentences_start_with_keyword: int     # 통 키워드로 시작 문장 수 (예: 6)
```

#### 2. KeywordAnalyzer (키워드 분석)
```python
class KeywordAnalyzer:
    def parse_keyword(self, keyword: str) -> Tuple[str, List[str]]:
        """통 키워드 → 조각 키워드 분리"""
        # "강남 맛집 추천" → ("강남 맛집 추천", ["강남", "맛집", "추천"])

    def count_whole_keyword(self, text: str, keyword: str) -> int:
        """띄어쓰기 기준 통 키워드 카운트"""
        # "강남 맛집 추천을" → 카운트 안 됨
        # "강남 맛집 추천 리스트" → 카운트 됨

    def count_piece_keywords(self, text: str, pieces: List[str]) -> Dict[str, int]:
        """조각 키워드 각각 카운트"""

    def count_sub_keywords(self, text: str, exclude: List[str]) -> int:
        """서브 키워드 개수 (2번 이상 등장, 통/조각 제외)"""
        # 중복 문장부호도 카운트: ^^, ??, ..., ;;
```

#### 3. ParticleHandler (조사 처리)
```python
class ParticleHandler:
    SINGLE_PARTICLES = ['를', '을', '가', '이', '는', '은', '에', '의']
    MULTI_PARTICLES = ['으로', '에서', '부터', '까지', '에게', '한테', '보다', '마저', '조차']

    def find_keyword_with_particle(self, text: str, keyword: str):
        """키워드+조사 찾기"""

    def fix_single_particle(self, text: str, keyword: str) -> str:
        """한글자 조사 → 우회 문장으로 수정 (AI 활용)"""
        # "강남 맛집 추천을 받기" → "강남 맛집 추천 리스트 확보"

    def fix_multi_particle(self, text: str, keyword: str) -> str:
        """두글자 조사 → 띄어쓰기 추가"""
        # "강남 맛집 추천으로" → "강남 맛집 추천 으로"
```

#### 4. SEOOptimizer (SEO 최적화)
```python
class SEOOptimizer:
    def optimize(self, text: str, config: SEOConfig) -> str:
        """SEO 설정에 맞게 원고 최적화"""

        # 1. 조사 처리 (통 키워드 카운트 가능하게)
        text = self._fix_particles(text, config.whole_keyword)

        # 2. 통 키워드 횟수 조정
        text = self._adjust_whole_keyword(text, config)

        # 3. 조각 키워드 횟수 조정
        text = self._adjust_piece_keywords(text, config)

        # 4. 첫 문단 조정
        text = self._adjust_first_paragraph(text, config)

        # 5. 통 키워드로 시작하는 문장 조정
        text = self._adjust_starting_sentences(text, config)

        # 6. 서브 키워드 조정
        text = self._adjust_sub_keywords(text, config)

        # 7. 글자수 조정
        text = self._adjust_char_count(text, config)

        # 8. 금칙어 치환
        if config.apply_forbidden_words:
            text = self._apply_forbidden_words(text)

        # 9. AI 자연스럽게 다듬기
        text = self._ai_polish(text, config)

        return text
```

#### 5. TemplateManager (글 구조 관리)
```python
class TemplateManager:
    def ensure_comment_request(self, text: str, keyword: str) -> str:
        """댓글 정보 공유 요청 문구 추가/확인"""
        # 초반부나 마지막에 "댓글로 정보 공유" 문구

    def ensure_question_flow(self, text: str, keyword: str) -> str:
        """질문/고민 구조 확인"""
        # 도입부 → 키워드 질문 → 댓글 요청
```

### Excel 구조

#### 기존 컬럼
- Column 3: 키워드 (통 키워드)
- Column 13: 원고

#### 추가 필요 컬럼 (SEO 설정)
- Column 14: 통 키워드 출현 횟수
- Column 15: 조각 키워드 설정 (JSON: {"강남": 10, "맛집": 4})
- Column 16: 글자수
- Column 17: 금칙어 치환 (O/X)
- Column 18: 첫문단 키워드 2회 (O/X)
- Column 19: 첫문단 키워드사이 2문장 (O/X)
- Column 20: 서브 키워드 개수
- Column 21: 키워드로 시작 문장 수

## 구현 순서

1. ✅ 요구사항 분석 및 설계 문서 작성
2. KeywordAnalyzer 구현 (띄어쓰기 기반 카운팅)
3. ParticleHandler 구현 (조사 처리)
4. SEOConfig 클래스 구현
5. SEOOptimizer 기본 구조 구현
6. 각 최적화 메서드 구현
7. TemplateManager 구현
8. Excel 처리 로직 수정
9. 통합 테스트

## 테스트 케이스

### 예시 1: "강남 맛집"

**입력 원고:**
```
강남 맛집을 찾고 있어요.
강남에서 맛집 찾기 힘들어요.
강남 맛집 추천 받고 싶어요.
```

**SEO 설정:**
- 통 키워드: "강남 맛집" 5번
- 조각 키워드: 강남 10번, 맛집 4번
- 글자수: 1000자
- 첫 문단 키워드 2회: O
- 키워드 시작 문장: 6개

**기대 출력:**
```
강남 맛집 추천 받고 싶어서 글 올려요.
요즘 회식 장소를 찾는데 강남 지역이 좋을 것 같아서요.
강남 맛집 정보 아시는 분 계실까요?
...
(통 키워드 정확히 5회)
(강남 10회, 맛집 4회)
(글자수 1000자)
```

## 주의사항

1. **카운팅 정확도**
   - 반드시 띄어쓰기 기준으로 카운트
   - 조사 붙은 것 제외

2. **자연스러움 유지**
   - 한글자 조사는 우회 문장으로
   - 억지로 키워드 넣지 말기

3. **글 구조**
   - 질문/고민 형태 유지
   - 댓글 요청 문구 포함
   - 제품 홍보 절대 NO

4. **서브 키워드**
   - 개수만 세면 됨
   - 중복 문장부호도 카운트
