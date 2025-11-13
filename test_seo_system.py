#!/usr/bin/env python3
"""
SEO 시스템 통합 테스트
"""

import os
from seo_optimizer import SEOOptimizer
from seo_config import SEOConfig


def test_basic_optimization():
    """기본 최적화 테스트"""

    print("="*80)
    print("SEO 시스템 통합 테스트")
    print("="*80)

    # API 키 확인
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\n⚠️ GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   일부 기능(AI 기반)은 동작하지 않습니다.\n")

    # Optimizer 생성
    optimizer = SEOOptimizer()

    # 테스트 케이스 1: "강남 맛집"
    print("\n" + "="*80)
    print("테스트 1: 강남 맛집")
    print("="*80)

    test_text1 = """강남 맛집을 찾고 있어요.
요즘 회식 장소로 강남에서 맛집 찾는 중인데요.
강남 맛집 추천 받고 싶어서 글 올려요.

회식 때마다 고민이에요.
좋은 강남 맛집 있으면 댓글로 알려주세요.
정말 궁금해요^^"""

    config1 = SEOConfig(
        whole_keyword="강남 맛집",
        whole_keyword_count=5,
        piece_keywords={"강남": 7, "맛집": 5},
        char_count=200,
        apply_forbidden_words=False,
        first_para_keyword_twice=True,
        first_para_two_sentences_between=False,
        sub_keyword_count=10,
        sentences_start_with_keyword=3,
    )

    print(f"\n원본 원고 ({len(test_text1)}자):")
    print("-"*80)
    print(test_text1)
    print("-"*80)

    result1 = optimizer.optimize(test_text1, config1)

    print(f"\n최적화된 원고 ({len(result1['optimized_text'])}자):")
    print("-"*80)
    print(result1['optimized_text'])
    print("-"*80)

    # 분석 결과
    print("\n분석 결과:")
    analysis1 = result1['analysis']
    print(f"  통 키워드: {analysis1['whole_keyword_count']}회 (목표: {config1.whole_keyword_count}회)")
    print(f"  조각 키워드: {analysis1['piece_keyword_counts']}")
    print(f"  서브 키워드: {analysis1['sub_keyword_count']}개 (목표: {config1.sub_keyword_count}개)")
    print(f"  키워드로 시작: {analysis1['sentences_start_with_keyword']}개 (목표: {config1.sentences_start_with_keyword}개)")
    print(f"  글자수: {analysis1['char_count']}자 (목표: {config1.char_count}자)")

    # 테스트 케이스 2: "갱년기홍조" (단일 단어)
    print("\n" + "="*80)
    print("테스트 2: 갱년기홍조 (단일 단어 키워드)")
    print("="*80)

    test_text2 = """갱년기홍조를 처음 겪고 있어요.
갱년기홍조가 이렇게 힘든지 몰랐어요.
갱년기홍조에 대해 알아보고 있는데, 정보가 부족하네요.

갱년기홍조 관리 방법 아시는 분 계실까요?
댓글로 정보 공유해주시면 감사하겠습니다."""

    config2 = SEOConfig(
        whole_keyword="갱년기홍조",
        whole_keyword_count=3,
        piece_keywords={},  # 단일 단어 → 조각 키워드 없음
        char_count=150,
        apply_forbidden_words=False,
        first_para_keyword_twice=False,
        first_para_two_sentences_between=False,
        sub_keyword_count=5,
        sentences_start_with_keyword=2,
    )

    print(f"\n원본 원고 ({len(test_text2)}자):")
    print("-"*80)
    print(test_text2)
    print("-"*80)

    result2 = optimizer.optimize(test_text2, config2)

    print(f"\n최적화된 원고 ({len(result2['optimized_text'])}자):")
    print("-"*80)
    print(result2['optimized_text'])
    print("-"*80)

    # 분석 결과
    print("\n분석 결과:")
    analysis2 = result2['analysis']
    print(f"  통 키워드: {analysis2['whole_keyword_count']}회 (목표: {config2.whole_keyword_count}회)")
    print(f"  조각 키워드: {analysis2['piece_keyword_counts']} (단일 단어)")
    print(f"  서브 키워드: {analysis2['sub_keyword_count']}개 (목표: {config2.sub_keyword_count}개)")
    print(f"  키워드로 시작: {analysis2['sentences_start_with_keyword']}개 (목표: {config2.sentences_start_with_keyword}개)")
    print(f"  글자수: {analysis2['char_count']}자 (목표: {config2.char_count}자)")

    print("\n" + "="*80)
    print("테스트 완료")
    print("="*80)


def test_keyword_counting():
    """키워드 카운팅 테스트"""

    print("\n" + "="*80)
    print("키워드 카운팅 정확도 테스트")
    print("="*80)

    from keyword_analyzer import KeywordAnalyzer

    analyzer = KeywordAnalyzer()

    # 테스트: 조사 붙은 것은 카운트 안 됨
    test_cases = [
        {
            'text': "강남 맛집을 찾아요. 강남 맛집 추천해주세요.",
            'keyword': "강남 맛집",
            'expected': 1,  # "강남 맛집 추천" 만 카운트
            'description': "조사 붙은 것 제외"
        },
        {
            'text': "강남 맛집 리스트를 보고 강남 맛집 가봤어요.",
            'keyword': "강남 맛집",
            'expected': 2,  # 둘 다 카운트
            'description': "띄어쓰기 있으면 카운트"
        },
        {
            'text': "강남 맛집으로 가고 강남 맛집 찾아요.",
            'keyword': "강남 맛집",
            'expected': 1,  # "강남 맛집 찾아요" 만 카운트 (으로는 두글자 조사지만 붙어있음)
            'description': "두글자 조사 붙으면 카운트 안 됨"
        },
    ]

    for i, test in enumerate(test_cases, 1):
        count = analyzer.count_whole_keyword(test['text'], test['keyword'])
        status = "✅" if count == test['expected'] else "❌"

        print(f"\n테스트 {i}: {test['description']}")
        print(f"  원문: {test['text']}")
        print(f"  키워드: {test['keyword']}")
        print(f"  결과: {count}회 / 기대: {test['expected']}회 {status}")


if __name__ == '__main__':
    # 키워드 카운팅 테스트 먼저
    test_keyword_counting()

    # 전체 최적화 테스트
    test_basic_optimization()
