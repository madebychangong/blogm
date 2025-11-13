"""
고급 블로그 원고 SEO 최적화 시스템
- 정교한 키워드 카운팅 (띄어쓰기 기준, 조사 처리)
- 서브키워드 자동 추출
- 글 확장 (목표 글자수 달성)
- 첫 문단 최적화
- 키워드로 시작하는 문장 생성
"""

import re
import random
from typing import Dict, List, Tuple, Set
from collections import Counter
import pandas as pd
from blog_optimizer import BlogOptimizer


class AdvancedSEOOptimizer(BlogOptimizer):
    """고급 SEO 최적화기 (BlogOptimizer 확장)"""

    def __init__(self, forbidden_words_file='금칙어 수정사항 모음.txt'):
        super().__init__(forbidden_words_file)

        # 한글 조사 목록 (한 글자 조사는 띄어쓰기 불가)
        self.one_char_particles = ['이', '가', '을', '를', '은', '는', '의', '에', '과', '와', '도', '만', '로', '으로']
        self.two_char_particles = ['에서', '부터', '까지', '에게', '한테', '처럼', '마다', '이나', '이든', '라도']

        # 글 확장 템플릿 (대폭 확장)
        self.expansion_templates = {
            '경험담': [
                "저도 비슷한 고민을 오랫동안 해왔는데요, 주변 분들도 많이 겪는 문제더라구요. 특히 나이가 들수록 이런 문제가 더 심해지는 것 같아서 걱정이에요. 젊었을 때는 전혀 신경 쓰지 않았던 부분인데 말이죠.",
                "사실 이 문제로 고민하면서 여러 방법을 다 찾아봤어요. 인터넷 검색도 많이 해보고, 지인들한테도 물어보고, 전문가 상담도 받아봤는데요. 각자 말하는 게 다 달라서 더 헷갈리더라고요.",
                "처음에는 어떻게 해야 할지 정말 막막했는데, 이것저것 알아보다 보니 조금씩 해결 방법이 보이더라고요. 물론 완벽한 해결책은 아니지만, 그래도 예전보다는 훨씬 나아진 것 같아요.",
                "비슷한 고민을 가진 분들과 이야기해보니 정말 공감되는 부분이 많더라구요. 혼자만 이런 고민을 하는 게 아니라는 걸 알게 되니 조금 위안이 되었어요. 함께 정보를 공유하면서 서로 도움을 주고받으면 좋겠어요.",
                "주변에서 좋다고 하는 방법들을 하나씩 시도해봤는데요, 사람마다 체질이 다르고 상황이 다르다 보니 효과도 각기 다르더라고요. 그래서 여러 가지를 시도해보면서 자신에게 맞는 방법을 찾는 게 중요한 것 같아요."
            ],
            '정보공유': [
                "혹시 같은 고민을 하시는 분들을 위해 제가 알아본 정보를 공유해드릴게요. 완벽한 정보는 아니지만, 조금이라도 도움이 되었으면 좋겠습니다.",
                "여러분도 비슷한 경험이 있으시다면 댓글로 공유해주세요. 서로의 경험을 나누다 보면 더 좋은 해결책을 찾을 수 있을 것 같아요.",
                "다른 분들의 경험담도 정말 궁금하네요. 댓글로 알려주시면 감사하겠습니다. 특히 실제로 효과를 보신 분들의 이야기를 듣고 싶어요.",
                "정보를 찾다 보니 생각보다 많은 분들이 이 문제로 고민하고 계시더라고요. 그래서 제가 알게 된 내용들을 정리해서 공유해드리면 좋을 것 같았어요. 혹시 추가로 궁금하신 점 있으면 댓글로 남겨주세요."
            ],
            '고민': [
                "이런 상황이 계속되니까 일상생활이 너무 불편하더라고요. 간단한 일상 동작 하나하나가 다 신경 쓰이고, 자꾸 의식하게 되니까 스트레스도 쌓이고요.",
                "이대로 방치하면 더 심해질 것 같아서 걱정이 앞서요. 지금 당장은 견딜 만하지만, 시간이 지날수록 악화될 수 있다는 생각에 불안하네요.",
                "전문가의 조언도 필요할 것 같은데, 여러분은 어떻게 생각하세요? 혹시 비슷한 경험 있으신 분들은 어떻게 대처하셨는지 궁금합니다.",
                "나이가 들수록 이런 문제들이 하나둘씩 생기는 것 같아요. 젊었을 때는 몰랐던 건강의 소중함을 이제야 깨닫게 되네요. 미리미리 관리하는 게 얼마나 중요한지 느껴요.",
                "가족들한테 짐이 될까봐 혼자 고민하는 경우가 많은데요, 사실 주변 사람들과 이야기를 나누는 것도 도움이 되는 것 같아요. 괜히 혼자 끙끙 앓는 것보다 훨씬 낫더라고요."
            ],
            '조언요청': [
                "혹시 이런 경험 있으신 분 계신가요? 어떻게 해결하셨는지 정말 궁금해요. 작은 팁이라도 공유해주시면 큰 도움이 될 것 같습니다.",
                "같은 고민을 하시는 분들끼리 정보를 공유하면 정말 좋을 것 같아요. 혼자 고민하는 것보다 함께 해결책을 찾아가는 게 훨씬 효과적이잖아요.",
                "댓글로 여러분의 이야기를 들려주세요. 성공 사례든 실패 사례든 모두 소중한 정보가 될 것 같습니다. 서로 도우면서 함께 개선해나갈 수 있으면 좋겠어요."
            ]
        }

    def count_keyword_accurate(self, text: str, keyword: str) -> int:
        """
        정교한 키워드 카운팅 (띄어쓰기 기준)

        규칙:
        - 띄어쓰기로 완전히 분리된 경우만 카운트
        - 조사가 붙으면 카운트 안 됨

        예시:
        - "강남 맛집 추천을" → 카운트 안 됨 (조사 "을" 붙음)
        - "강남 맛집 추천 리스트" → 카운트 1회
        """
        if not keyword or pd.isna(keyword):
            return 0

        count = 0
        # 키워드 앞뒤에 공백이나 문장부호가 있는 경우만 매치
        # 정규식: (^|[\s\n]) + 키워드 + ([\s\n,.]|$)
        pattern = r'(?:^|[\s\n])(' + re.escape(keyword) + r')(?=[\s\n,.!?]|$)'
        matches = re.findall(pattern, text)
        count = len(matches)

        return count

    def extract_piece_keywords(self, keyword: str) -> List[str]:
        """통키워드에서 조각키워드 추출"""
        if not keyword or pd.isna(keyword):
            return []

        # 띄어쓰기로 분리
        pieces = keyword.split()
        # 2글자 이상만 (조사 제외)
        pieces = [p for p in pieces if len(p) >= 2]
        return pieces

    def count_piece_keywords(self, text: str, piece_keywords: List[str]) -> Dict[str, int]:
        """조각키워드 개별 카운팅"""
        counts = {}
        for piece in piece_keywords:
            # 각 조각을 단어 단위로 카운트
            # 정규식: (^|[\s\n]) + 조각 + ([\s\n]|$)
            pattern = r'(?:^|[\s\n])(' + re.escape(piece) + r')(?=[\s\n,.!?]|$)'
            matches = re.findall(pattern, text)
            counts[piece] = len(matches)

        return counts

    def extract_subkeywords(self, text: str, exclude_keywords: List[str]) -> Dict[str, int]:
        """
        서브키워드 추출 (2번 이상 등장하는 단어)

        규칙:
        - 통키워드, 조각키워드 제외
        - 2글자 이상 단어
        - 2회 이상 등장
        - 중복 문장부호도 포함 (^^, ??, ... 등)
        """
        # 1. 일반 단어 추출
        words = re.findall(r'[가-힣]{2,}', text)
        word_counts = Counter(words)

        # 2. 문장부호 패턴 추출
        punctuation_patterns = re.findall(r'([.!?;]{2,}|[^\w\s]{2,})', text)
        punct_counts = Counter(punctuation_patterns)

        # 3. 합치기
        all_counts = {**word_counts, **punct_counts}

        # 4. 제외 키워드 필터링
        exclude_set = set(exclude_keywords)
        subkeywords = {}

        for word, count in all_counts.items():
            if count >= 2 and word not in exclude_set:
                subkeywords[word] = count

        return subkeywords

    def count_keyword_start_sentences(self, text: str, keyword: str) -> int:
        """키워드로 시작하는 문장의 수"""
        if not keyword or pd.isna(keyword):
            return 0

        # 문장 분리 (., !, ?, \n 기준)
        sentences = re.split(r'[.!?\n]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        count = 0
        for sentence in sentences:
            if sentence.startswith(keyword):
                count += 1

        return count

    def optimize_first_paragraph(self, text: str, keyword: str, target_keyword_count: int = 2) -> str:
        """
        첫 문단 최적화

        규칙:
        - 첫 문단에 키워드 2회 반복
        - 키워드 사이에 최소 2문장 삽입
        """
        if not keyword or pd.isna(keyword):
            return text

        # 문단 분리
        paragraphs = text.split('\n\n')
        if not paragraphs:
            return text

        first_para = paragraphs[0]

        # 첫 문단의 키워드 카운트
        current_count = self.count_keyword_accurate(first_para, keyword)

        if current_count >= target_keyword_count:
            return text  # 이미 충족

        # 키워드 추가 필요
        sentences = re.split(r'([.!?])', first_para)
        sentences = [''.join(sentences[i:i+2]) for i in range(0, len(sentences)-1, 2)]
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 3:
            # 문장이 너무 적으면 추가
            sentences.append(f"{keyword}에 대해 더 알아보고 싶어서 여러 정보를 찾아봤어요.")

        # 첫 문장과 세 번째 문장에 키워드 삽입 (사이에 1-2문장)
        if current_count == 0:
            # 키워드가 하나도 없으면
            sentences[0] = f"{keyword}에 대해 궁금한 점이 많습니다. " + sentences[0]
            if len(sentences) >= 3:
                sentences[2] = f"{keyword} 관련해서 경험 있으신 분들의 이야기가 듣고 싶어요. " + sentences[2]
            else:
                sentences.append(f"{keyword} 관련해서 경험 있으신 분들의 이야기가 듣고 싶어요.")

        # 재결합
        paragraphs[0] = ' '.join(sentences)
        return '\n\n'.join(paragraphs)

    def generate_keyword_start_sentences(self, keyword: str, count: int = 3) -> List[str]:
        """키워드로 시작하는 문장 생성"""
        templates = [
            f"{keyword}는 요즘 많은 분들이 관심 갖는 주제인 것 같아요.",
            f"{keyword}에 대해 알아보니 생각보다 다양한 정보가 있더라고요.",
            f"{keyword} 관련해서 여러분의 경험담을 듣고 싶습니다.",
            f"{keyword}를 처음 알게 되었을 때 정말 신기했어요.",
            f"{keyword}로 고민하시는 분들께 도움이 되었으면 좋겠습니다.",
            f"{keyword}에 관심이 생긴 건 최근의 일이에요.",
        ]

        # 조사 처리 (자연스럽게)
        selected = random.sample(templates, min(count, len(templates)))
        return selected

    def expand_content(self, text: str, keyword: str, target_length: int) -> str:
        """
        글 확장 (목표 글자수 달성)

        전략:
        - 기존 글의 톤 유지
        - 경험담, 정보공유, 고민 템플릿 활용
        - 키워드 자연스럽게 삽입
        - 반복적으로 확장 (목표 글자수 달성까지)
        """
        current_length = len(text)

        if current_length >= target_length:
            return text

        # 문단 분리
        paragraphs = text.split('\n\n')

        # 확장을 여러 번 반복 (목표 달성까지)
        max_iterations = 5
        iteration = 0

        while len(text) < target_length and iteration < max_iterations:
            iteration += 1
            need_length = target_length - len(text)

            # 확장할 내용 생성
            expansion_parts = []

            # 1. 경험담 추가 (여러 개)
            if need_length > 100:
                for _ in range(min(2, len(self.expansion_templates['경험담']))):
                    expansion_parts.append(random.choice(self.expansion_templates['경험담']))

            # 2. 키워드 포함 문장 추가 (여러 개)
            if need_length > 200:
                keyword_sentences = self.generate_keyword_start_sentences(keyword, 3)
                expansion_parts.extend(keyword_sentences)

            # 3. 정보공유 추가 (여러 개)
            if need_length > 400:
                for _ in range(2):
                    expansion_parts.append(random.choice(self.expansion_templates['정보공유']))

            # 4. 고민 추가 (여러 개)
            if need_length > 600:
                for _ in range(2):
                    expansion_parts.append(random.choice(self.expansion_templates['고민']))

            # 5. 조언요청 추가
            if need_length > 800:
                expansion_parts.append(random.choice(self.expansion_templates['조언요청']))

            # 6. 추가 키워드 문장
            if need_length > 1000:
                more_keyword_sentences = self.generate_keyword_start_sentences(keyword, 2)
                expansion_parts.extend(more_keyword_sentences)

            # 확장 내용 삽입
            if expansion_parts:
                # 중간 또는 끝에 삽입 (랜덤)
                insert_positions = [
                    len(paragraphs) // 3,
                    len(paragraphs) // 2,
                    len(paragraphs) * 2 // 3,
                    len(paragraphs) - 1
                ]

                for i, part in enumerate(expansion_parts):
                    insert_pos = insert_positions[i % len(insert_positions)]
                    paragraphs.insert(insert_pos + i, part)

                text = '\n\n'.join(paragraphs)

            # 무한 루프 방지
            if len(text) <= current_length + 50:
                break
            current_length = len(text)

        # 마지막에 댓글 유도 문구 (없으면 추가)
        if "댓글" not in text[-200:]:
            paragraphs = text.split('\n\n')
            paragraphs.append(random.choice([
                "여러분의 경험담이나 좋은 정보가 있으시면 댓글로 꼭 공유해주세요!",
                "같은 고민을 하시는 분들끼리 정보 공유하면 좋을 것 같아요. 댓글 부탁드립니다!",
                "혹시 좋은 방법 아시는 분 계시면 댓글로 알려주시면 정말 감사하겠습니다!"
            ]))
            text = '\n\n'.join(paragraphs)

        return text

    def fix_particle_spacing(self, text: str, keyword: str) -> str:
        """
        조사 띄어쓰기 수정

        규칙:
        - 한 글자 조사: 띄어쓰기 제거 (부자연스러움)
        - 두 글자 이상 조사: 띄어쓰기 유지

        단, 키워드 카운팅을 위해 필요한 경우 우회 표현 사용
        """
        # 한 글자 조사가 키워드 뒤에 띄어져 있으면 붙이기
        for particle in self.one_char_particles:
            # "키워드 조사" → "키워드+조사"로 변경
            pattern = re.escape(keyword) + r'\s+(' + particle + r')'

            # 단, 카운팅이 필요하면 우회 표현으로 변경
            matches = re.findall(pattern, text)
            for match in matches:
                # "키워드 을" → "키워드 관련 정보를"
                if particle in ['을', '를']:
                    replacement = f"{keyword} 관련 정보를"
                    text = re.sub(pattern, replacement, text, count=1)
                elif particle in ['이', '가']:
                    replacement = f"{keyword}가"
                    text = re.sub(pattern, replacement, text, count=1)
                else:
                    # 그냥 붙이기
                    replacement = f"{keyword}{particle}"
                    text = re.sub(pattern, replacement, text, count=1)

        return text

    def analyze_seo_status(self, text: str, keyword: str) -> Dict:
        """현재 SEO 상태 분석"""
        # 통키워드 카운트
        whole_keyword_count = self.count_keyword_accurate(text, keyword)

        # 조각키워드 추출 및 카운트
        piece_keywords = self.extract_piece_keywords(keyword)
        piece_counts = self.count_piece_keywords(text, piece_keywords)

        # 서브키워드 추출
        exclude_list = [keyword] + piece_keywords
        subkeywords = self.extract_subkeywords(text, exclude_list)

        # 키워드로 시작하는 문장 수
        keyword_start_count = self.count_keyword_start_sentences(text, keyword)

        # 글자수
        char_count = len(text)

        return {
            'char_count': char_count,
            'whole_keyword_count': whole_keyword_count,
            'piece_keywords': piece_keywords,
            'piece_counts': piece_counts,
            'subkeyword_count': len(subkeywords),
            'subkeywords': subkeywords,
            'keyword_start_sentences': keyword_start_count
        }

    def optimize_advanced(
        self,
        text: str,
        keyword: str,
        brand: str = '',
        title: str = '',
        target_char_count: int = 2000,
        target_whole_keyword: int = 5,
        target_piece_keywords: Dict[str, int] = None,
        target_subkeyword_count: int = 20,
        target_keyword_start: int = 3
    ) -> Dict:
        """
        고급 최적화 실행

        Args:
            text: 원고
            keyword: 통키워드
            brand: 브랜드
            title: 제목
            target_char_count: 목표 글자수
            target_whole_keyword: 목표 통키워드 반복수
            target_piece_keywords: 목표 조각키워드 반복수 {"강남": 10, "맛집": 4}
            target_subkeyword_count: 목표 서브키워드 개수
            target_keyword_start: 목표 키워드로 시작하는 문장 수
        """
        original_text = text

        # 1. 기본 최적화 (금칙어, AI 패턴 등)
        basic_result = self.optimize_text(text, keyword, brand, title)
        text = basic_result['optimized_text']

        # 2. 현재 상태 분석
        current_status = self.analyze_seo_status(text, keyword)

        # 3. 글 확장 (목표 글자수)
        if current_status['char_count'] < target_char_count:
            text = self.expand_content(text, keyword, target_char_count)

        # 4. 첫 문단 최적화 (키워드 2회)
        text = self.optimize_first_paragraph(text, keyword, 2)

        # 5. 조사 띄어쓰기 수정
        text = self.fix_particle_spacing(text, keyword)

        # 6. 키워드로 시작하는 문장 추가
        current_keyword_start = self.count_keyword_start_sentences(text, keyword)
        if current_keyword_start < target_keyword_start:
            need = target_keyword_start - current_keyword_start
            keyword_sentences = self.generate_keyword_start_sentences(keyword, need)

            # 문단 중간에 삽입
            paragraphs = text.split('\n\n')
            insert_pos = len(paragraphs) // 2
            for sentence in keyword_sentences:
                paragraphs.insert(insert_pos, sentence)
                insert_pos += 1

            text = '\n\n'.join(paragraphs)

        # 7. 최종 상태 분석
        final_status = self.analyze_seo_status(text, keyword)

        # 8. SEO 체크
        c_rank = self.check_c_rank_criteria(
            text,
            final_status['whole_keyword_count'],
            len(basic_result['hashtags'])
        )

        return {
            'optimized_text': text,
            'optimized_title': basic_result['optimized_title'],
            'hashtags': basic_result['hashtags'],
            'original_status': current_status,
            'final_status': final_status,
            'c_rank_check': c_rank,
            'changes': basic_result['changes']
        }


def main():
    """테스트"""
    optimizer = AdvancedSEOOptimizer()

    # 테스트 텍스트
    test_text = """
# 팔꿈치 쿠션 보호대 관련해서 사용해보신 분 계신가요?

팔꿈치 쿠션 보호대를 최근에 알게 되어서 정말 고민이 많습니다.
사실 저는 무릎 통증으로 고생하고 있는 50대인데요,
의자에서 일어날 때마다 "아이고" 소리가 절로 나올 정도로 힘들어요.
"""

    keyword = "팔꿈치 쿠션 보호대"

    # 현재 상태 분석
    status = optimizer.analyze_seo_status(test_text, keyword)

    print("=" * 80)
    print("SEO 상태 분석")
    print("=" * 80)
    print(f"글자수: {status['char_count']}자")
    print(f"통키워드 출현: {status['whole_keyword_count']}회")
    print(f"조각키워드: {status['piece_keywords']}")
    print(f"조각키워드 출현: {status['piece_counts']}")
    print(f"서브키워드 개수: {status['subkeyword_count']}개")
    print(f"키워드로 시작하는 문장: {status['keyword_start_sentences']}개")

    print("\n" + "=" * 80)
    print("최적화 실행")
    print("=" * 80)

    result = optimizer.optimize_advanced(
        text=test_text,
        keyword=keyword,
        brand="초록입환",
        target_char_count=1500,
        target_whole_keyword=5,
        target_subkeyword_count=15,
        target_keyword_start=3
    )

    print(f"\n최적화된 텍스트 (앞부분 500자):")
    print(result['optimized_text'][:500])
    print("...")

    print(f"\n최종 상태:")
    print(f"  글자수: {result['final_status']['char_count']}자")
    print(f"  통키워드: {result['final_status']['whole_keyword_count']}회")
    print(f"  서브키워드: {result['final_status']['subkeyword_count']}개")
    print(f"  C랭크: {result['c_rank_check']['rank']}등급 ({result['c_rank_check']['score']}점)")


if __name__ == '__main__':
    main()
