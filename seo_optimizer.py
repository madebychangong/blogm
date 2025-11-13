#!/usr/bin/env python3
"""
SEO 최적화 엔진

SEO 설정에 맞게 원고 최적화
"""

import os
import re
from typing import Optional, Dict, List
import google.generativeai as genai

from seo_config import SEOConfig
from keyword_analyzer import KeywordAnalyzer
from particle_handler import ParticleHandler
from forbidden_words_loader import ForbiddenWordsLoader


class SEOOptimizer:
    """SEO 기준에 맞게 원고 최적화"""

    def __init__(self, api_key: Optional[str] = None, forbidden_words_file: str = '금칙어 리스트.xlsx'):
        """
        초기화

        Args:
            api_key: Gemini API 키
            forbidden_words_file: 금칙어 리스트 Excel 파일
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        # 컴포넌트 초기화
        self.analyzer = KeywordAnalyzer()
        self.particle_handler = ParticleHandler(self.api_key)
        self.forbidden_loader = ForbiddenWordsLoader(forbidden_words_file)

        # Gemini 초기화
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-pro')
        else:
            print("⚠️ Gemini API 키 없음 - AI 기능 제한됨")
            self.model = None

    def _fix_particles(self, text: str, keyword: str) -> str:
        """
        조사 처리 (통 키워드 카운트 가능하게)

        Args:
            text: 원고
            keyword: 통 키워드

        Returns:
            수정된 원고
        """
        return self.particle_handler.fix_all_particles(text, keyword)

    def _adjust_whole_keyword_count(self, text: str, config: SEOConfig) -> str:
        """
        통 키워드 출현 횟수 조정

        Args:
            text: 원고
            config: SEO 설정

        Returns:
            수정된 원고
        """
        keyword = config.whole_keyword
        target_count = config.whole_keyword_count
        current_count = self.analyzer.count_whole_keyword(text, keyword)

        print(f"\n통 키워드 조정: '{keyword}'")
        print(f"  현재: {current_count}회 → 목표: {target_count}회")

        if current_count == target_count:
            print(f"  ✅ 이미 목표 달성!")
            return text

        if current_count < target_count:
            # 키워드 추가 필요
            print(f"  ➕ {target_count - current_count}회 추가 필요")
            text = self._add_whole_keyword(text, keyword, target_count - current_count)
        else:
            # 키워드 감소 필요
            print(f"  ➖ {current_count - target_count}회 감소 필요")
            text = self._reduce_whole_keyword(text, keyword, current_count - target_count)

        return text

    def _add_whole_keyword(self, text: str, keyword: str, count: int) -> str:
        """
        통 키워드 추가 (AI 활용)

        Args:
            text: 원고
            keyword: 통 키워드
            count: 추가할 횟수

        Returns:
            수정된 원고
        """
        if not self.model:
            print("  ⚠️ AI 없음 - 키워드 추가 불가")
            return text

        prompt = f"""당신은 자연스러운 블로그 글 편집자입니다.

# 요청

아래 원고에 "{keyword}" 키워드를 자연스럽게 {count}회 추가하세요.

**제약 조건:**
1. 원본 글의 구조와 의미 유지
2. 키워드는 반드시 띄어쓰기로 구분되어야 함 (조사 붙이지 말 것)
3. 억지로 넣지 말고 자연스럽게
4. 블로그 말투 유지

**원고:**
{text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 출력
수정된 원고만 출력하세요. 설명 없이.
"""

        try:
            response = self.model.generate_content(prompt)
            if response.text:
                return response.text.strip()
        except Exception as e:
            print(f"  ⚠️ AI 오류: {e}")

        return text

    def _reduce_whole_keyword(self, text: str, keyword: str, count: int) -> str:
        """
        통 키워드 감소

        Args:
            text: 원고
            keyword: 통 키워드
            count: 감소할 횟수

        Returns:
            수정된 원고
        """
        # 통 키워드를 찾아서 뒤에서부터 제거 (앞쪽 키워드 보존)
        # 패턴: 키워드 뒤에 공백이나 문장부호
        pattern = re.escape(keyword) + r'(?=\s|[.,!?;:\)\]\}]|$)'

        matches = list(re.finditer(pattern, text))

        if len(matches) <= count:
            print(f"  ⚠️ 제거할 키워드가 부족함")
            return text

        # 뒤에서부터 제거
        removed = 0
        for match in reversed(matches):
            if removed >= count:
                break

            # 키워드를 제거하고 문맥에 맞는 대명사로 교체
            start, end = match.span()
            before = text[:start]
            after = text[end:]

            # 간단히 "이것"으로 교체
            text = before + "이것" + after
            removed += 1

        return text

    def _adjust_piece_keywords(self, text: str, config: SEOConfig) -> str:
        """
        조각 키워드 출현 횟수 조정

        Args:
            text: 원고
            config: SEO 설정

        Returns:
            수정된 원고
        """
        if not config.piece_keywords:
            return text

        print(f"\n조각 키워드 조정:")

        for piece, target_count in config.piece_keywords.items():
            current_count = self.analyzer.count_piece_keywords(text, [piece])[piece]
            print(f"  '{piece}': {current_count}회 → {target_count}회")

            if current_count == target_count:
                print(f"    ✅ 이미 목표 달성!")
                continue

            # TODO: 조각 키워드 추가/감소 로직
            # 통 키워드보다 복잡함 - 나중에 구현

        return text

    def _adjust_first_paragraph(self, text: str, config: SEOConfig) -> str:
        """
        첫 문단 조정

        Args:
            text: 원고
            config: SEO 설정

        Returns:
            수정된 원고
        """
        keyword = config.whole_keyword

        first_para = self.analyzer.get_first_paragraph(text)
        first_para_count = self.analyzer.count_whole_keyword(first_para, keyword)
        sentences_between = self.analyzer.count_sentences_between_keywords(first_para, keyword)

        print(f"\n첫 문단 조정:")
        print(f"  키워드 출현: {first_para_count}회")

        # 1. 첫 문단 키워드 2회 체크
        if config.first_para_keyword_twice:
            if first_para_count < 2:
                print(f"  ➕ 첫 문단에 키워드 {2 - first_para_count}회 더 필요")
                # TODO: AI로 키워드 추가
            elif first_para_count > 2:
                print(f"  ➖ 첫 문단에 키워드 {first_para_count - 2}회 제거 필요")
                # TODO: 키워드 제거
            else:
                print(f"  ✅ 첫 문단 키워드 2회 충족!")

        # 2. 키워드 사이 2문장 체크
        if config.first_para_two_sentences_between:
            if sentences_between < 2:
                print(f"  ➕ 키워드 사이 {2 - sentences_between}개 문장 더 필요")
                # TODO: AI로 문장 추가
            elif sentences_between > 2:
                print(f"  ➖ 키워드 사이 {sentences_between - 2}개 문장 제거 필요")
                # TODO: 문장 제거
            else:
                print(f"  ✅ 키워드 사이 2문장 충족!")

        return text

    def _adjust_starting_sentences(self, text: str, config: SEOConfig) -> str:
        """
        통 키워드로 시작하는 문장 조정

        Args:
            text: 원고
            config: SEO 설정

        Returns:
            수정된 원고
        """
        keyword = config.whole_keyword
        target_count = config.sentences_start_with_keyword
        current_count = self.analyzer.find_sentences_starting_with_keyword(text, keyword)

        print(f"\n키워드로 시작하는 문장:")
        print(f"  현재: {current_count}개 → 목표: {target_count}개")

        if current_count == target_count:
            print(f"  ✅ 이미 목표 달성!")
        else:
            # TODO: AI로 문장 시작 부분 수정
            print(f"  ⚠️ 구현 필요")

        return text

    def _adjust_sub_keywords(self, text: str, config: SEOConfig) -> str:
        """
        서브 키워드 조정

        Args:
            text: 원고
            config: SEO 설정

        Returns:
            수정된 원고
        """
        keyword = config.whole_keyword
        pieces = config.piece_keywords.keys() if config.piece_keywords else []
        exclude = [keyword] + list(pieces)

        current_count = self.analyzer.count_sub_keywords(text, exclude)
        target_count = config.sub_keyword_count

        print(f"\n서브 키워드:")
        print(f"  현재: {current_count}개 → 목표: {target_count}개")

        if current_count == target_count:
            print(f"  ✅ 이미 목표 달성!")
        else:
            # TODO: 서브 키워드 조정 (복잡함 - 나중에)
            print(f"  ⚠️ 구현 필요")

        return text

    def _adjust_char_count(self, text: str, config: SEOConfig) -> str:
        """
        글자수 조정

        Args:
            text: 원고
            config: SEO 설정

        Returns:
            수정된 원고
        """
        current_count = len(text)
        target_count = config.char_count

        print(f"\n글자수:")
        print(f"  현재: {current_count}자 → 목표: {target_count}자")

        # ±10% 허용 범위
        tolerance = target_count * 0.1
        if abs(current_count - target_count) <= tolerance:
            print(f"  ✅ 허용 범위 내!")
            return text

        if current_count < target_count:
            print(f"  ➕ {target_count - current_count}자 추가 필요")
            # TODO: AI로 내용 확장
        else:
            print(f"  ➖ {current_count - target_count}자 감소 필요")
            # TODO: AI로 내용 축소

        return text

    def _apply_forbidden_words(self, text: str) -> str:
        """
        금칙어 치환

        Args:
            text: 원고

        Returns:
            수정된 원고
        """
        print(f"\n금칙어 치환:")

        replacements = self.forbidden_loader.get_replacements()
        replaced_count = 0

        for forbidden, alternatives in replacements.items():
            if forbidden in text:
                # 첫 번째 대체어 사용
                replacement = alternatives[0] if alternatives else forbidden
                text = text.replace(forbidden, replacement)
                replaced_count += 1
                print(f"  '{forbidden}' → '{replacement}'")

        print(f"  총 {replaced_count}개 치환 완료")

        return text

    def _ai_polish(self, text: str, config: SEOConfig) -> str:
        """
        AI로 자연스럽게 다듬기

        Args:
            text: 원고
            config: SEO 설정

        Returns:
            수정된 원고
        """
        if not self.model:
            print("\n⚠️ AI 없음 - 다듬기 생략")
            return text

        print(f"\n🤖 AI 다듬기 중...")

        keyword = config.whole_keyword

        prompt = f"""당신은 블로그 글의 어색한 부분만 살짝 고치는 편집자입니다.

⚠️ **핵심 원칙: 원본을 거의 그대로 두세요!**

# 입력 원고
키워드: {keyword}

{text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 요청

**어색한 부분만 최소한으로 수정:**
1. 조사 오류 수정
2. 중복 표현 제거
3. 부자연스러운 단어 교체
4. 원본 구조는 절대 변경 금지

**출력:**
수정된 원고만 출력하세요. 설명 없이.
"""

        try:
            response = self.model.generate_content(prompt)
            if response.text:
                print(f"  ✅ 다듬기 완료")
                return response.text.strip()
        except Exception as e:
            print(f"  ⚠️ AI 오류: {e}")

        return text

    def optimize(self, text: str, config: SEOConfig) -> Dict:
        """
        SEO 설정에 맞게 원고 최적화

        Args:
            text: 원고
            config: SEO 설정

        Returns:
            {
                'optimized_text': 최적화된 원고,
                'analysis': 분석 결과
            }
        """
        print(f"\n{'='*80}")
        print(f"SEO 최적화 시작")
        print(f"{'='*80}")
        print(config)
        print(f"{'='*80}\n")

        # 1. 조사 처리 (통 키워드 카운트 가능하게)
        text = self._fix_particles(text, config.whole_keyword)

        # 2. 통 키워드 횟수 조정
        text = self._adjust_whole_keyword_count(text, config)

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

        # 최종 분석
        analysis = self.analyzer.analyze(text, config.whole_keyword)

        print(f"\n{'='*80}")
        print(f"SEO 최적화 완료")
        print(f"{'='*80}")
        print(f"통 키워드: {analysis['whole_keyword_count']}회 (목표: {config.whole_keyword_count}회)")
        print(f"조각 키워드: {analysis['piece_keyword_counts']}")
        print(f"서브 키워드: {analysis['sub_keyword_count']}개 (목표: {config.sub_keyword_count}개)")
        print(f"키워드로 시작 문장: {analysis['sentences_start_with_keyword']}개 (목표: {config.sentences_start_with_keyword}개)")
        print(f"글자수: {analysis['char_count']}자 (목표: {config.char_count}자)")
        print(f"{'='*80}\n")

        return {
            'optimized_text': text,
            'analysis': analysis,
        }


def test_seo_optimizer():
    """테스트"""

    # API 키 확인
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수를 설정해주세요.")
        return

    optimizer = SEOOptimizer()

    # 테스트 원고
    test_text = """강남 맛집을 찾고 있어요.
요즘 회식 장소로 강남에서 맛집 찾는 중인데요.
강남 맛집 추천 받고 싶어서 글 올려요.

회식 장소로 좋은 곳 있으면 댓글로 알려주세요.
정말 궁금해요^^"""

    # SEO 설정
    config = SEOConfig(
        whole_keyword="강남 맛집",
        whole_keyword_count=5,
        piece_keywords={"강남": 10, "맛집": 4},
        char_count=1000,
        apply_forbidden_words=False,
        first_para_keyword_twice=True,
        first_para_two_sentences_between=True,
        sub_keyword_count=20,
        sentences_start_with_keyword=6,
    )

    # 최적화
    result = optimizer.optimize(test_text, config)

    print("\n" + "=" * 80)
    print("최종 결과")
    print("=" * 80)
    print(result['optimized_text'])
    print("=" * 80)


if __name__ == '__main__':
    test_seo_optimizer()
