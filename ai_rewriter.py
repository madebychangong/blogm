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
        """재구성 프롬프트 생성 - 사람이 쓴 것처럼 자연스럽게"""

        # 금칙어 리스트 (주요 금칙어만)
        forbidden_words = [
            "네요", "가격", "광고", "구매", "병원", "진단", "효과",
            "상담", "시술", "의사", "환자", "판매", "투자", "후회",
            "보험", "재발", "대출", "비용", "의문", "의심", "약효",
            "산부인과", "부작용", "홍보성", "의구심"
        ]

        prompt = f"""당신은 30-50대 블로그 사용자가 직접 작성한 것처럼 자연스러운 경험담을 쓰는 전문가입니다.

# 입력된 원고 (금칙어 자동 치환됨)
키워드: {keyword}

원고:
{text}

# 핵심 목표: **사람이 직접 쓴 것처럼 자연스럽게!**

## 1. 금칙어 회피 (절대 규칙)
❌ 절대 사용 금지: {', '.join(forbidden_words)}
✅ 치환된 단어를 더 자연스럽게 문맥에 맞게 재구성

**어색한 치환 → 자연스러운 문장:**
- "경비이 부담돼서" → "금액이 부담되어서" / "돈이 많이 들어서"
- "궁금하다도 들고" → "궁금한 마음도 들고" / "의심스럽기도 하고"
- "그런 모습이 시작된" → "그런 느낌이 시작된" / "그런 증세가 나타난"
- "변화 보신 제품" → "도움 받은 제품" / "효과 본 방법"

## 2. 사람처럼 자연스러운 말투 (핵심!)
✅ **구어체 자연스럽게:**
- "~더라고요", "~거든요", "~던데요", "~잖아요" 적절히 섞기
- "솔직히", "진짜", "정말", "아무튼" 같은 자연스러운 부사 사용
- "근데", "그래서", "그런데" 등 접속사로 흐름 만들기

✅ **문장 종결어미 다양화:**
- ~어요 (30%) / ~더라고요 (20%) / ~거든요 (15%)
- ~죠 (10%) / ~해요 (10%) / ~던데요 (10%) / ~습니다 (5%)
- "~요"만 반복하지 말 것!

✅ **실제 경험담처럼:**
- "저는 ~인데", "제 경우엔", "저한테는" 등 주관적 표현
- 감정 표현: "힘들어서", "고민이 많아서", "답답해서"
- 구체적 시간: "최근에", "요즘", "몇 달 전부터"

## 3. 키워드 자연스럽게 유지
- 키워드 "{keyword}"는 정확히 2-3회만 사용
- 키워드 뒤 조사 붙이지 않기 (X: {keyword}가, O: {keyword} 사용하면)
- 대신 "이거", "이런 거", "제품" 등으로 자연스럽게 대체

## 4. 조사 오류 반드시 수정
❌ 어색: "경비이", "궁금하다도", "병의원이라는"
✅ 자연: "금액이", "궁금한데도", "병원에서"

**치환 후 조사 확인:**
- 받침 있음: ~이, ~을, ~과
- 받침 없음: ~가, ~를, ~와

## 5. 문맥에 맞는 자연스러운 재구성
**단순 치환을 넘어서:**
- "그런 모습" → 문맥에 따라 "그런 증세", "그런 느낌", "이런 상태"
- "변화" → 문맥에 따라 "도움", "개선", "효과", "차이"
- "병의원" → 문맥에 따라 "병원", "산부인과 쪽", "전문의"

**문장 전체를 자연스럽게:**
- Before: "이거 그런 모습이 시작된 지"
- After: "이런 증세가 나타난 지" / "이런 느낌이 시작된 지"

## 6. AI 느낌 제거
❌ 피해야 할 AI 표현:
- "~하시길 바랍니다", "~하시기 바랍니다"
- "~것으로 생각됩니다", "~것으로 보입니다"
- 과도하게 정중한 표현

✅ 사람다운 표현:
- "~해보세요", "~하면 좋을 것 같아요"
- "제 생각엔", "제 경험상", "저는 ~더라고요"
- 편하고 친근한 말투

## 7. 원본 유지 사항
- 핵심 내용과 의미는 절대 변경 금지
- 원본과 비슷한 길이 유지 (±50자 이내)
- 단락 구조 유지
- 경험담의 진솔함과 감정 그대로 유지

# 출력
재구성된 원고만 출력하세요. 설명, 주석, 제목은 불필요합니다.
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
