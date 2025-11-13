#!/usr/bin/env python3
"""
조사 처리 모듈

한글자 조사: 우회 문장으로 수정 (AI 활용)
두글자 이상 조사: 띄어쓰기 추가
"""

import re
from typing import List, Tuple, Optional
import google.generativeai as genai
import os


class ParticleHandler:
    """키워드 뒤의 조사 처리"""

    # 한글자 조사 (띄어쓰기하면 부자연스러움 → 우회 필요)
    SINGLE_PARTICLES = ['를', '을', '가', '이', '는', '은', '에', '의', '도', '만', '와', '과']

    # 두글자 이상 조사 (띄어쓰기 OK)
    MULTI_PARTICLES = ['으로', '에서', '부터', '까지', '에게', '한테', '보다', '마저', '조차',
                       '이나', '이며', '이라', '처럼', '같이', '마다', '라는', '이란']

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화

        Args:
            api_key: Gemini API 키 (없으면 환경변수 GEMINI_API_KEY 사용)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if self.api_key:
            # Gemini 설정
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
        else:
            print("⚠️ Gemini API 키 없음 - AI 우회 문장 생성 불가")
            self.model = None

    def find_keyword_with_single_particle(self, text: str, keyword: str) -> List[Tuple[str, str]]:
        """
        키워드+한글자 조사 찾기

        Args:
            text: 원고
            keyword: 통 키워드

        Returns:
            [(전체 패턴, 조사), ...] 예: [("강남 맛집을", "을"), ...]
        """
        results = []

        for particle in self.SINGLE_PARTICLES:
            pattern = re.escape(keyword) + particle
            matches = re.finditer(pattern, text)

            for match in matches:
                results.append((match.group(), particle))

        return results

    def find_keyword_with_multi_particle(self, text: str, keyword: str) -> List[Tuple[str, str]]:
        """
        키워드+두글자 조사 찾기 (띄어쓰기 없는 경우)

        Args:
            text: 원고
            keyword: 통 키워드

        Returns:
            [(전체 패턴, 조사), ...] 예: [("강남 맛집으로", "으로"), ...]
        """
        results = []

        for particle in self.MULTI_PARTICLES:
            # 띄어쓰기 없이 붙은 경우만 찾기
            pattern = re.escape(keyword) + particle
            matches = re.finditer(pattern, text)

            for match in matches:
                # 이미 띄어쓰기가 있는지 확인 (키워드 공백 조사)
                before_match = match.start() - 1
                if before_match >= 0 and text[before_match] == ' ':
                    # 이미 띄어쓰기 있음 - 스킵
                    continue

                results.append((match.group(), particle))

        return results

    def create_workaround_prompt(self, sentence: str, keyword: str, particle: str) -> str:
        """
        우회 문장 생성 프롬프트

        Args:
            sentence: 원본 문장
            keyword: 통 키워드
            particle: 조사

        Returns:
            프롬프트
        """
        prompt = f"""당신은 자연스러운 문장 수정 전문가입니다.

# 요청

아래 문장에서 "{keyword}{particle}"를 자연스럽게 수정하세요.

**제약 조건:**
1. "{keyword}" 뒤에 한글자 조사 "{particle}"가 바로 붙으면 SEO에서 카운트되지 않습니다
2. "{keyword} {particle}" 처럼 띄어쓰기하면 매우 부자연스럽습니다
3. 따라서 문장 구조를 바꿔서 "{keyword}"가 카운트되도록 해야 합니다

**수정 방법:**
- "{keyword}{particle}" 부분을 "{keyword} [추가 단어]"로 수정
- 조사는 추가 단어 뒤에 붙이기
- 문장의 의미는 최대한 유지
- 자연스러운 블로그 말투 유지

**예시:**
```
입력: "강남 맛집을 찾고 있어요"
출력: "강남 맛집 리스트를 찾고 있어요"
→ "강남 맛집" 카운트 가능! ✅

입력: "갱년기 홍조가 심해요"
출력: "갱년기 홍조 증세가 심해요"
→ "갱년기 홍조" 카운트 가능! ✅

입력: "피부과를 방문했어요"
출력: "피부과 병원을 방문했어요"
→ "피부과" 카운트 가능! ✅
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 원본 문장
{sentence}

# 수정할 부분
"{keyword}{particle}" → "{keyword} [추가 단어]"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 출력
수정된 문장만 출력하세요. 설명 없이.
"""
        return prompt

    def fix_single_particle_with_ai(self, text: str, keyword: str) -> str:
        """
        한글자 조사 → AI로 우회 문장 생성

        Args:
            text: 원고
            keyword: 통 키워드

        Returns:
            수정된 원고
        """
        if not self.model:
            print("⚠️ Gemini API 키 없음 - 한글자 조사 처리 불가")
            return text

        # 키워드+한글자 조사 찾기
        patterns = self.find_keyword_with_single_particle(text, keyword)

        if not patterns:
            return text

        print(f"\n🔧 한글자 조사 발견: {len(patterns)}개")

        # 문장 단위로 분리
        sentences = re.split(r'([.!?])', text)
        # 구분자 포함해서 다시 합치기
        sentences = [''.join(sentences[i:i+2]) for i in range(0, len(sentences)-1, 2)]
        if len(text) > 0 and text[-1] not in '.!?':
            # 마지막 문장이 마침표 없으면 추가
            sentences.append(''.join(sentences[-2:]) if len(sentences) >= 2 else text)

        modified_text = text

        for pattern, particle in patterns:
            # 이 패턴이 포함된 문장 찾기
            for sentence in sentences:
                if pattern in sentence:
                    print(f"  - 수정 중: '{pattern}' in '{sentence.strip()}'")

                    # AI로 우회 문장 생성
                    try:
                        prompt = self.create_workaround_prompt(sentence, keyword, particle)
                        response = self.model.generate_content(prompt)

                        if response.text:
                            new_sentence = response.text.strip()
                            modified_text = modified_text.replace(sentence, new_sentence)
                            print(f"    → '{new_sentence.strip()}'")
                            break

                    except Exception as e:
                        print(f"    ⚠️ AI 오류: {e}")
                        continue

        return modified_text

    def fix_multi_particle(self, text: str, keyword: str) -> str:
        """
        두글자 조사 → 띄어쓰기 추가

        Args:
            text: 원고
            keyword: 통 키워드

        Returns:
            수정된 원고
        """
        # 키워드+두글자 조사 찾기 (띄어쓰기 없는 경우)
        patterns = self.find_keyword_with_multi_particle(text, keyword)

        if not patterns:
            return text

        print(f"\n✏️ 두글자 조사 발견: {len(patterns)}개 - 띄어쓰기 추가")

        modified_text = text

        for pattern, particle in patterns:
            # "키워드조사" → "키워드 조사"
            new_pattern = keyword + ' ' + particle
            modified_text = modified_text.replace(pattern, new_pattern)
            print(f"  - '{pattern}' → '{new_pattern}'")

        return modified_text

    def fix_all_particles(self, text: str, keyword: str) -> str:
        """
        모든 조사 처리 (한글자 + 두글자)

        Args:
            text: 원고
            keyword: 통 키워드

        Returns:
            수정된 원고
        """
        print(f"\n{'='*80}")
        print(f"조사 처리: {keyword}")
        print(f"{'='*80}")

        # 1. 두글자 조사 먼저 처리 (간단)
        text = self.fix_multi_particle(text, keyword)

        # 2. 한글자 조사 처리 (AI 필요)
        text = self.fix_single_particle_with_ai(text, keyword)

        print(f"{'='*80}\n")

        return text


def test_particle_handler():
    """테스트"""

    # API 키 확인
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수를 설정해주세요.")
        return

    handler = ParticleHandler()

    # 테스트 1: 두글자 조사 띄어쓰기
    print("=" * 80)
    print("테스트 1: 두글자 조사 띄어쓰기")
    print("=" * 80)

    test_text1 = "강남 맛집으로 리꼬르라는 레스토랑을 다녀왔어요."
    keyword1 = "강남 맛집"

    print(f"\n원본: {test_text1}")

    result1 = handler.fix_multi_particle(test_text1, keyword1)

    print(f"\n수정: {result1}")
    print(f"기대: 강남 맛집 으로 리꼬르라는 레스토랑을 다녀왔어요.")

    # 테스트 2: 한글자 조사 우회
    print("\n" + "=" * 80)
    print("테스트 2: 한글자 조사 우회 (AI)")
    print("=" * 80)

    test_text2 = "강남 맛집을 찾고 있어요. 강남 맛집가 많다고 들었어요."
    keyword2 = "강남 맛집"

    print(f"\n원본: {test_text2}")

    result2 = handler.fix_single_particle_with_ai(test_text2, keyword2)

    print(f"\n수정: {result2}")

    # 테스트 3: 전체 처리
    print("\n" + "=" * 80)
    print("테스트 3: 전체 처리")
    print("=" * 80)

    test_text3 = """강남 맛집을 찾고 있어요.
강남 맛집으로 추천 받고 싶어요.
강남 맛집가 많다고 해서 궁금해요."""

    keyword3 = "강남 맛집"

    print(f"\n원본:\n{test_text3}")

    result3 = handler.fix_all_particles(test_text3, keyword3)

    print(f"\n최종 결과:\n{result3}")


if __name__ == '__main__':
    test_particle_handler()
