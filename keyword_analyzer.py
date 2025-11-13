#!/usr/bin/env python3
"""
키워드 분석 모듈

띄어쓰기 기준 키워드 카운팅:
- 통 키워드: 전체 키워드 문구
- 조각 키워드: 통 키워드의 각 단어
- 서브 키워드: 2번 이상 등장하는 단어 (통/조각 제외)
"""

import re
from typing import List, Dict, Tuple, Set
from collections import Counter


class KeywordAnalyzer:
    """키워드 분석 및 카운팅"""

    # 한글자 조사
    SINGLE_PARTICLES = ['를', '을', '가', '이', '는', '은', '에', '의', '도', '만', '와', '과']

    # 두글자 이상 조사
    MULTI_PARTICLES = ['으로', '에서', '부터', '까지', '에게', '한테', '보다', '마저', '조차',
                       '이나', '이며', '이라', '라는', '이란', '처럼', '같이', '마다']

    def parse_keyword(self, keyword: str) -> Tuple[str, List[str]]:
        """
        통 키워드 → 조각 키워드 분리

        Args:
            keyword: 통 키워드 (예: "강남 맛집 추천")

        Returns:
            (통 키워드, [조각 키워드들])
            예: ("강남 맛집 추천", ["강남", "맛집", "추천"])
        """
        pieces = keyword.split()

        if len(pieces) == 1:
            # 단일 단어: 조각 키워드 없음
            return keyword, []
        else:
            # 띄어쓰기 포함: 조각 키워드 분리
            return keyword, pieces

    def count_whole_keyword(self, text: str, keyword: str) -> int:
        """
        띄어쓰기 기준 통 키워드 카운트

        규칙:
        - "강남 맛집 추천을" → 카운트 안 됨 (조사 '을' 바로 붙음)
        - "강남 맛집 추천 리스트" → 카운트 됨 (띄어쓰기 있음)

        Args:
            text: 원고
            keyword: 통 키워드

        Returns:
            출현 횟수
        """
        count = 0

        # 키워드를 정규식으로 찾기
        # 키워드 뒤에 공백, 문장부호, 또는 문자열 끝이 와야 함
        pattern = re.escape(keyword) + r'(?=\s|[.,!?;:\)\]\}]|$)'

        matches = re.finditer(pattern, text)

        for match in matches:
            end_pos = match.end()

            # 키워드 뒤에 바로 한글자 조사가 붙었는지 확인
            if end_pos < len(text):
                next_char = text[end_pos]

                # 한글자 조사가 바로 붙으면 카운트 안 함
                if next_char in self.SINGLE_PARTICLES:
                    continue

            # 카운트
            count += 1

        return count

    def count_piece_keywords(self, text: str, pieces: List[str]) -> Dict[str, int]:
        """
        조각 키워드 각각 카운트

        Args:
            text: 원고
            pieces: 조각 키워드 리스트 (예: ["강남", "맛집", "추천"])

        Returns:
            {단어: 출현횟수}
        """
        result = {}

        for piece in pieces:
            count = 0

            # 문장부호를 공백으로 치환해서 단어 분리
            normalized_text = re.sub(r'[.,!?;:\(\[\{\)\]\}]', ' ', text)

            # 띄어쓰기 기준으로 분리
            words = normalized_text.split()

            # 조각 키워드 카운트
            count = words.count(piece)

            result[piece] = count

        return result

    def count_sub_keywords(self, text: str, exclude_words: List[str]) -> int:
        """
        서브 키워드 개수 카운트

        규칙:
        - 원고에 2번 이상 등장하는 단어
        - 통/조각 키워드 제외
        - 중복 문장부호도 카운트 (^^, ??, ..., ;;)
        - ?? 와 ??? 는 다른 서브 키워드

        Args:
            text: 원고
            exclude_words: 제외할 단어 (통/조각 키워드)

        Returns:
            서브 키워드 개수
        """
        # 1. 단어 추출
        words = []

        # 한글 단어 추출 (2글자 이상)
        korean_words = re.findall(r'[가-힣]{2,}', text)
        words.extend(korean_words)

        # 영어 단어 추출 (2글자 이상)
        english_words = re.findall(r'[a-zA-Z]{2,}', text)
        words.extend(english_words)

        # 숫자 추출
        numbers = re.findall(r'\d+', text)
        words.extend(numbers)

        # 2. 중복 문장부호 추출 (2개 이상 연속)
        punctuations = re.findall(r'[.,!?;:^\-~]{2,}', text)
        words.extend(punctuations)

        # 3. 출현 횟수 카운트
        word_counts = Counter(words)

        # 4. 2번 이상 등장하는 단어만 필터링
        sub_keywords = []
        exclude_set = set(exclude_words)

        for word, count in word_counts.items():
            if count >= 2 and word not in exclude_set:
                sub_keywords.append(word)

        return len(sub_keywords)

    def find_sentences_starting_with_keyword(self, text: str, keyword: str) -> int:
        """
        통 키워드로 시작하는 문장 개수

        Args:
            text: 원고
            keyword: 통 키워드

        Returns:
            문장 개수
        """
        # 문장 분리 (마침표, 느낌표, 물음표 기준)
        sentences = re.split(r'[.!?]\s*', text)

        count = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence.startswith(keyword):
                count += 1

        return count

    def get_first_paragraph(self, text: str) -> str:
        """
        첫 문단 추출

        Args:
            text: 원고

        Returns:
            첫 문단
        """
        # 빈 줄로 문단 구분
        paragraphs = text.split('\n\n')

        if paragraphs:
            return paragraphs[0].strip()
        else:
            # 문단 구분 없으면 전체 텍스트
            return text.strip()

    def count_sentences_between_keywords(self, paragraph: str, keyword: str) -> int:
        """
        첫 문단에서 첫 번째와 두 번째 키워드 사이의 문장 개수

        Args:
            paragraph: 첫 문단
            keyword: 통 키워드

        Returns:
            사이 문장 개수 (-1: 키워드가 2회 미만)
        """
        # 키워드 위치 찾기
        first_pos = paragraph.find(keyword)
        if first_pos == -1:
            return -1

        second_pos = paragraph.find(keyword, first_pos + len(keyword))
        if second_pos == -1:
            return -1

        # 두 키워드 사이의 텍스트
        between = paragraph[first_pos + len(keyword):second_pos]

        # 문장 개수 세기 (마침표, 느낌표, 물음표)
        sentences = re.split(r'[.!?]', between)

        # 빈 문자열 제외
        sentences = [s.strip() for s in sentences if s.strip()]

        return len(sentences)

    def analyze(self, text: str, keyword: str) -> Dict:
        """
        전체 키워드 분석

        Args:
            text: 원고
            keyword: 통 키워드

        Returns:
            분석 결과 딕셔너리
        """
        # 통/조각 키워드 분리
        whole_keyword, piece_keywords = self.parse_keyword(keyword)

        # 카운팅
        whole_count = self.count_whole_keyword(text, whole_keyword)
        piece_counts = self.count_piece_keywords(text, piece_keywords) if piece_keywords else {}

        # 서브 키워드
        exclude = [whole_keyword] + piece_keywords
        sub_keyword_count = self.count_sub_keywords(text, exclude)

        # 첫 문단
        first_para = self.get_first_paragraph(text)
        first_para_keyword_count = self.count_whole_keyword(first_para, whole_keyword)
        sentences_between = self.count_sentences_between_keywords(first_para, whole_keyword)

        # 키워드로 시작하는 문장
        sentences_start_with_keyword = self.find_sentences_starting_with_keyword(text, whole_keyword)

        # 글자수
        char_count = len(text)

        return {
            'whole_keyword': whole_keyword,
            'whole_keyword_count': whole_count,
            'piece_keywords': piece_keywords,
            'piece_keyword_counts': piece_counts,
            'sub_keyword_count': sub_keyword_count,
            'first_paragraph': first_para,
            'first_para_keyword_count': first_para_keyword_count,
            'sentences_between_keywords': sentences_between,
            'sentences_start_with_keyword': sentences_start_with_keyword,
            'char_count': char_count,
        }


def test_analyzer():
    """테스트"""

    analyzer = KeywordAnalyzer()

    # 테스트 케이스 1: 통 키워드 카운팅
    print("=" * 80)
    print("테스트 1: 통 키워드 카운팅 (띄어쓰기 기준)")
    print("=" * 80)

    test_text = """강남 맛집을 찾고 있어요.
강남 맛집 추천 받고 싶어요.
강남에서 맛집 많이 가봤어요.
강남 맛집 리스트 있으신가요?"""

    keyword = "강남 맛집"

    count = analyzer.count_whole_keyword(test_text, keyword)
    print(f"\n키워드: {keyword}")
    print(f"원고:\n{test_text}")
    print(f"\n통 키워드 출현: {count}회")
    print(f"기대값: 2회 ('강남 맛집 추천', '강남 맛집 리스트')")
    print(f"✅ 통과!" if count == 2 else f"❌ 실패!")

    # 테스트 케이스 2: 조각 키워드 카운팅
    print("\n" + "=" * 80)
    print("테스트 2: 조각 키워드 카운팅")
    print("=" * 80)

    pieces = analyzer.parse_keyword(keyword)[1]
    piece_counts = analyzer.count_piece_keywords(test_text, pieces)

    print(f"\n조각 키워드: {pieces}")
    print(f"출현 횟수:")
    for piece, count in piece_counts.items():
        print(f"  - {piece}: {count}회")

    # 테스트 케이스 3: 서브 키워드
    print("\n" + "=" * 80)
    print("테스트 3: 서브 키워드 개수")
    print("=" * 80)

    test_text2 = """강남 맛집 추천 받고 싶어요.
요즘 회식 장소로 강남 맛집 찾고 있어요.
회식 장소 추천해주세요.
추천 부탁드려요^^
정말 궁금해요??"""

    exclude = [keyword] + pieces
    sub_count = analyzer.count_sub_keywords(test_text2, exclude)

    print(f"\n원고:\n{test_text2}")
    print(f"\n제외 키워드: {exclude}")
    print(f"서브 키워드 개수: {sub_count}개")
    print(f"예상: '요즘', '회식', '장소', '추천', '받고', '찾고', '정말', '부탁드려요', '궁금해요', ^^, ?? 등")

    # 테스트 케이스 4: 전체 분석
    print("\n" + "=" * 80)
    print("테스트 4: 전체 분석")
    print("=" * 80)

    test_text3 = """강남 맛집 추천 받고 싶어서 글 올려요.
요즘 회식 장소를 찾는데 강남 지역이 좋을 것 같아서요.
강남 맛집 정보 아시는 분 계실까요?

회식 장소로 좋은 곳 있으면 댓글로 공유해주세요^^
정말 궁금해요??"""

    result = analyzer.analyze(test_text3, keyword)

    print(f"\n분석 결과:")
    print(f"  통 키워드: {result['whole_keyword']}")
    print(f"  통 키워드 출현: {result['whole_keyword_count']}회")
    print(f"  조각 키워드 출현: {result['piece_keyword_counts']}")
    print(f"  서브 키워드 개수: {result['sub_keyword_count']}개")
    print(f"  첫 문단 키워드: {result['first_para_keyword_count']}회")
    print(f"  첫 문단 키워드 사이 문장: {result['sentences_between_keywords']}개")
    print(f"  키워드로 시작 문장: {result['sentences_start_with_keyword']}개")
    print(f"  글자수: {result['char_count']}자")


if __name__ == '__main__':
    test_analyzer()
