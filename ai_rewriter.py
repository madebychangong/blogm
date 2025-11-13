#!/usr/bin/env python3
"""
Gemini API를 사용한 자연스러운 블로그 원고 재구성
- 금칙어 회피
- 자연스러운 구어체
- "요" 반복 방지
"""

import os
import google.generativeai as genai
from typing import Optional


class AIRewriter:
    """Gemini API를 사용한 원고 재구성"""

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화

        Args:
            api_key: Gemini API 키 (없으면 환경변수 GEMINI_API_KEY 사용)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError(
                "Gemini API 키가 필요합니다. "
                "환경변수 GEMINI_API_KEY를 설정하거나 api_key 파라미터를 전달하세요."
            )

        # Gemini 설정
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def create_prompt(self, text: str, keyword: str) -> str:
        """재구성 프롬프트 생성"""

        # 금칙어 리스트 (주요 금칙어만)
        forbidden_words = [
            "네요", "가격", "광고", "구매", "병원", "진단", "효과",
            "상담", "시술", "의사", "환자", "판매", "투자", "후회",
            "보험", "재발", "대출", "비용", "의문", "의심"
        ]

        prompt = f"""당신은 네이버 블로그 글을 자연스럽게 재구성하는 전문가입니다.

# 입력된 원고
키워드: {keyword}

원고:
{text}

# 작업 지시사항

1. **금칙어 절대 사용 금지**
   - 다음 단어들을 절대 사용하지 마세요: {', '.join(forbidden_words)}
   - 이미 치환된 단어들을 유지하되, 더 자연스럽게 바꾸세요

2. **자연스러운 블로그 말투**
   - "~요" 반복 최소화 (최대 30% 이하)
   - 다양한 문장 종결어미 사용:
     * ~어요 / ~습니다 / ~해요 / ~죠 / ~거든요 / ~더라고요
     * ~아요 / ~던데요 / ~하고요 / ~거예요
   - 자연스러운 구어체 유지

3. **키워드 "{keyword}" 유지**
   - 키워드는 정확히 2-3회만 사용
   - 키워드 뒤에 조사(를/을/가/이/에/의) 붙이지 않기
   - "이거", "이것", "제품" 등으로 대체 가능

4. **문장 흐름 개선**
   - 어색한 표현 수정
   - 문장 길이 다양화
   - 단락 구조 유지

5. **원래 의미와 분량 유지**
   - 핵심 내용 변경 금지
   - 원본과 비슷한 길이 유지
   - 경험담과 감정 유지

# 출력 형식
재구성된 원고만 출력하세요. 설명이나 주석은 불필요합니다.
"""
        return prompt

    def rewrite(self, text: str, keyword: str) -> str:
        """
        원고를 자연스럽게 재구성

        Args:
            text: 치환된 원고
            keyword: 키워드

        Returns:
            재구성된 원고
        """
        try:
            prompt = self.create_prompt(text, keyword)
            response = self.model.generate_content(prompt)

            if response.text:
                return response.text.strip()
            else:
                print("⚠️ AI 재구성 실패: 응답 없음")
                return text

        except Exception as e:
            print(f"⚠️ AI 재구성 오류: {e}")
            return text


def test_rewriter():
    """테스트"""

    # API 키 확인
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수를 설정해주세요.")
        print("   export GEMINI_API_KEY='your-api-key'")
        return

    rewriter = AIRewriter()

    # 테스트 원고
    test_text = """팔꿈치 쿠션 보호대 최근에 알게 되어서 진짜 고민돼요.
사실 저는 무릎 통증으로 불편함을 느끼는 50대인데요,
의자에서 일어날 때마다 "아이고" 소리가 절로 나올 정도로 힘들어요.
이거 사용하면 관절 통증에 도움이 된다는 이야기를 우연히 듣게 되었는데,
정말 약효가 있을지 의구심이 들어서 궁금해서 글 남겨요."""

    keyword = "팔꿈치 쿠션 보호대"

    print("=" * 80)
    print("AI 재구성 테스트")
    print("=" * 80)
    print(f"\n키워드: {keyword}")
    print(f"\n원본:")
    print(test_text)

    print(f"\n재구성 중...")
    result = rewriter.rewrite(test_text, keyword)

    print(f"\n재구성 결과:")
    print(result)

    # 금칙어 확인
    forbidden_check = ["네요", "가격", "광고", "구매", "병원", "효과"]
    print(f"\n금칙어 체크:")
    for word in forbidden_check:
        if word in result:
            print(f"  ❌ '{word}' 발견됨!")
        else:
            print(f"  ✅ '{word}' 없음")

    # 키워드 출현 확인
    count = result.count(keyword)
    print(f"\n키워드 출현: {count}회")


if __name__ == '__main__':
    test_rewriter()
