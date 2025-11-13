#!/usr/bin/env python3
"""
SEO 설정 클래스

각 글별로 다른 SEO 기준 적용
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class SEOConfig:
    """글별 SEO 설정"""

    # 통 키워드 설정
    whole_keyword: str                      # 통 키워드 (예: "강남 맛집 추천")
    whole_keyword_count: int                # 출현 횟수 (예: 5)

    # 조각 키워드 설정
    piece_keywords: Dict[str, int]          # {단어: 출현횟수} (예: {"강남": 10, "맛집": 4})

    # 글 설정
    char_count: int                         # 글자수 (예: 1000)
    apply_forbidden_words: bool             # 금칙어 치환 (True/False)

    # 첫 문단 설정
    first_para_keyword_twice: bool          # 첫 문단 통키워드 2회 (True/False)
    first_para_two_sentences_between: bool  # 키워드 사이 2문장 이상 (True/False)

    # 서브 키워드 설정
    sub_keyword_count: int                  # 서브 키워드 목록 수 (예: 20)

    # 문장 구조
    sentences_start_with_keyword: int       # 통 키워드로 시작 문장 수 (예: 6)

    @classmethod
    def from_dict(cls, data: Dict) -> 'SEOConfig':
        """
        딕셔너리에서 SEOConfig 생성

        Args:
            data: 설정 딕셔너리

        Returns:
            SEOConfig 인스턴스
        """
        return cls(
            whole_keyword=data['whole_keyword'],
            whole_keyword_count=data['whole_keyword_count'],
            piece_keywords=data.get('piece_keywords', {}),
            char_count=data['char_count'],
            apply_forbidden_words=data['apply_forbidden_words'],
            first_para_keyword_twice=data['first_para_keyword_twice'],
            first_para_two_sentences_between=data['first_para_two_sentences_between'],
            sub_keyword_count=data['sub_keyword_count'],
            sentences_start_with_keyword=data['sentences_start_with_keyword'],
        )

    def to_dict(self) -> Dict:
        """
        SEOConfig를 딕셔너리로 변환

        Returns:
            설정 딕셔너리
        """
        return {
            'whole_keyword': self.whole_keyword,
            'whole_keyword_count': self.whole_keyword_count,
            'piece_keywords': self.piece_keywords,
            'char_count': self.char_count,
            'apply_forbidden_words': self.apply_forbidden_words,
            'first_para_keyword_twice': self.first_para_keyword_twice,
            'first_para_two_sentences_between': self.first_para_two_sentences_between,
            'sub_keyword_count': self.sub_keyword_count,
            'sentences_start_with_keyword': self.sentences_start_with_keyword,
        }

    def __str__(self) -> str:
        """문자열 표현"""
        return f"""SEO 설정:
  통 키워드: {self.whole_keyword} ({self.whole_keyword_count}회)
  조각 키워드: {self.piece_keywords}
  글자수: {self.char_count}자
  금칙어 치환: {'O' if self.apply_forbidden_words else 'X'}
  첫문단 키워드 2회: {'O' if self.first_para_keyword_twice else 'X'}
  첫문단 키워드사이 2문장: {'O' if self.first_para_two_sentences_between else 'X'}
  서브 키워드: {self.sub_keyword_count}개
  키워드로 시작 문장: {self.sentences_start_with_keyword}개"""


def test_seo_config():
    """테스트"""

    # 예시 1: "강남 맛집" 글 설정
    config1 = SEOConfig(
        whole_keyword="강남 맛집",
        whole_keyword_count=5,
        piece_keywords={"강남": 10, "맛집": 4},
        char_count=1000,
        apply_forbidden_words=True,
        first_para_keyword_twice=True,
        first_para_two_sentences_between=True,
        sub_keyword_count=20,
        sentences_start_with_keyword=6,
    )

    print("=" * 80)
    print("테스트 1: SEOConfig 생성")
    print("=" * 80)
    print(config1)

    # 딕셔너리 변환
    print("\n" + "=" * 80)
    print("테스트 2: 딕셔너리 변환")
    print("=" * 80)
    config_dict = config1.to_dict()
    print(config_dict)

    # 딕셔너리에서 복원
    print("\n" + "=" * 80)
    print("테스트 3: 딕셔너리에서 복원")
    print("=" * 80)
    config2 = SEOConfig.from_dict(config_dict)
    print(config2)

    # 예시 2: "갱년기홍조" 글 설정 (단일 단어)
    config3 = SEOConfig(
        whole_keyword="갱년기홍조",
        whole_keyword_count=3,
        piece_keywords={},  # 단일 단어 → 조각 키워드 없음
        char_count=800,
        apply_forbidden_words=True,
        first_para_keyword_twice=False,
        first_para_two_sentences_between=False,
        sub_keyword_count=15,
        sentences_start_with_keyword=4,
    )

    print("\n" + "=" * 80)
    print("테스트 4: 단일 단어 키워드")
    print("=" * 80)
    print(config3)


if __name__ == '__main__':
    test_seo_config()
