"""
블로그 원고 키워드 띄어쓰기 최적화
- 키워드 뒤 1글자 조사 제거/수정
- 검색 노출 최적화
"""

import re
import random
from typing import Dict, List
import pandas as pd
from blog_optimizer import BlogOptimizer


class KeywordSpacingOptimizer(BlogOptimizer):
    """키워드 띄어쓰기 최적화"""

    def __init__(self, forbidden_words_file='금칙어 수정사항 모음.txt'):
        super().__init__(forbidden_words_file)

        # 1글자 조사 목록
        self.one_char_particles = {
            '을': ['', ' 관련', ' 관련해서'],
            '를': ['', ' 관련', ' 관련해서'],
            '이': ['', '가'],
            '가': ['', '가'],  # "가" 는 유지 가능
            '은': ['', '는'],
            '는': ['', '는'],
            '에': [' 관해서', ' 관련해서', ''],
            '의': [' 관련', ''],
            '과': [' 및', ' 그리고'],
            '와': [' 및', ' 그리고'],
            '도': [' 역시', '도'],
            '만': [' 위주로', '만'],
            '로': [' 통해', '로'],
        }

        # 2글자 이상 조사/접속사 (띄어쓰기만)
        self.multi_char_particles = [
            '에서', '부터', '까지', '에게', '한테',
            '처럼', '마다', '이나', '이든', '라도',
            '라는', '이란', '라고', '라면'
        ]

    def fix_keyword_spacing(self, text: str, keyword: str) -> str:
        """
        키워드 뒤 1글자 조사를 수정

        규칙:
        1. 키워드 + 1글자 조사 → 키워드 + 대체어 또는 제거
        2. 키워드 + 2글자 이상 → 키워드 + 띄어쓰기 + 2글자

        예시:
        - "고관절영양제에" → "고관절영양제 관해서"
        - "고관절영양제를" → "고관절영양제" 또는 "고관절영양제 관련"
        - "고관절영양제라는" → "고관절영양제 라는"
        """
        if not keyword or pd.isna(keyword):
            return text

        modified_text = text
        changes = []

        # 1. 1글자 조사 처리
        for particle, replacements in self.one_char_particles.items():
            pattern = f'({re.escape(keyword)}){particle}([^가-힣]|$)'
            matches = re.findall(pattern, modified_text)

            if matches:
                # 랜덤 대체어 선택
                replacement = random.choice(replacements)
                # 대체
                modified_text = re.sub(
                    pattern,
                    f'{keyword}{replacement}\\2',
                    modified_text
                )
                changes.append(f'{keyword}{particle} → {keyword}{replacement}')

        # 2. 2글자 이상 조사 띄어쓰기 처리
        for particle in self.multi_char_particles:
            # 붙어있는 경우만 찾기
            pattern = f'({re.escape(keyword)})({particle})'
            matches = re.findall(pattern, modified_text)

            if matches:
                # 띄어쓰기 추가
                modified_text = re.sub(
                    pattern,
                    f'{keyword} \\2',
                    modified_text
                )
                changes.append(f'{keyword}{particle} → {keyword} {particle}')

        return modified_text

    def optimize_for_search(self, text: str, keyword: str, brand: str = '') -> Dict:
        """
        검색 노출 최적화 (길이 유지)

        작업:
        1. 키워드 띄어쓰기 수정
        2. 금칙어 치환
        3. AI 표현 제거
        4. 길이는 유지!
        """
        if pd.isna(text) or not text:
            return {
                'optimized_text': '',
                'original_length': 0,
                'optimized_length': 0,
                'changes': []
            }

        original_text = text
        original_length = len(text)
        all_changes = []

        # 1. 키워드 띄어쓰기 수정
        text = self.fix_keyword_spacing(text, keyword)
        all_changes.append('✅ 키워드 띄어쓰기 수정')

        # 2. 금칙어 치환
        text, forbidden_changes = self.replace_forbidden_words(text)
        if forbidden_changes:
            all_changes.extend(forbidden_changes)

        # 3. AI 패턴 다양화
        text, ai_changes = self.diversify_ai_patterns(text)
        if ai_changes:
            all_changes.extend(ai_changes)

        # 4. 자연스러운 변형
        text = self.add_natural_variations(text)

        # 5. 해시태그 생성
        hashtags = self.generate_hashtags(keyword, brand)

        # 6. 제목 생성
        title = self.generate_title(keyword, text)

        # 7. 키워드 카운팅 (정확도 체크)
        keyword_count = text.count(keyword)

        return {
            'optimized_text': text,
            'optimized_title': title,
            'original_length': original_length,
            'optimized_length': len(text),
            'changes': all_changes,
            'keyword_count': keyword_count,
            'hashtags': hashtags,
            'length_diff': len(text) - original_length
        }
