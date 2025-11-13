"""
블로그 원고 키워드 띄어쓰기 최적화 (템플릿 패턴 기반)
- 검색 노출 최적화
- 키워드+조사 제거
- 키워드 출현 2-3회로 감소
"""

import re
import random
from typing import Dict, List
import pandas as pd
from blog_optimizer import BlogOptimizer


class SearchOptimizer(BlogOptimizer):
    """검색 노출 최적화 (키워드 띄어쓰기 + 키워드 감소)"""

    def __init__(self, forbidden_words_file='금칙어 수정사항 모음.txt'):
        super().__init__(forbidden_words_file)

    def remove_hashtag_title(self, text: str) -> str:
        """# 제목 삭제"""
        lines = text.split('\n')
        if lines and lines[0].strip().startswith('#'):
            return '\n'.join(lines[1:]).strip()
        return text

    def remove_keyword_particles(self, text: str, keyword: str) -> str:
        """
        키워드+조사 제거 또는 수정

        전략:
        1. 키워드+를/을 → 키워드 + 동사 또는 제거
        2. 키워드+가/이 → 키워드 또는 문장 재구성
        3. 키워드+에 → 키워드 관해서 또는 제거
        4. 키워드+라는 → 키워드 라는 (띄어쓰기)
        """
        if not keyword or pd.isna(keyword):
            return text

        modified = text

        # 1. 키워드+를/을 처리
        # "키워드를 먹고" → "키워드 먹고"
        # "키워드를 최근에" → "키워드 라는 걸 최근에"
        pattern1 = f'({re.escape(keyword)})[를을]\\s+'
        modified = re.sub(pattern1, f'{keyword} ', modified)

        # 2. 키워드+가/이 처리
        # "키워드가 좋다" → "키워드 좋다" 또는 "키워드 먹으면"
        pattern2 = f'({re.escape(keyword)})[가이]\\s+'

        def replace_subject(match):
            # 랜덤하게 제거 또는 대체
            choices = [
                f'{keyword} ',
                f'{keyword} 먹으면 ',
                f'{keyword} 사용하면 ',
            ]
            return random.choice(choices)

        modified = re.sub(pattern2, replace_subject, modified)

        # 3. 키워드+에 처리
        # "키워드에 대해" → 문장 삭제 또는 "키워드 관해서"
        pattern3 = f'({re.escape(keyword)})에\\s+대해'
        modified = re.sub(pattern3, '', modified)  # 제목이므로 삭제

        pattern3b = f'({re.escape(keyword)})에\\s+'
        modified = re.sub(pattern3b, f'{keyword} 관해서 ', modified)

        # 4. 키워드+의 처리
        pattern4 = f'({re.escape(keyword)})의\\s+'
        modified = re.sub(pattern4, f'{keyword} 관련 ', modified)

        # 5. 키워드+라는 → 키워드 라는 (띄어쓰기)
        pattern5 = f'({re.escape(keyword)})라는'
        modified = re.sub(pattern5, f'{keyword} 라는', modified)

        # 6. 키워드+는/은 일부 제거
        # 너무 많으면 일부만 제거
        pattern6 = f'({re.escape(keyword)})[는은]\\s+'
        count = len(re.findall(pattern6, modified))
        if count > 1:
            # 첫 번째만 제거
            modified = re.sub(pattern6, f'{keyword} ', modified, count=1)

        return modified

    def reduce_keyword_frequency(self, text: str, keyword: str, target_count: int = 2) -> str:
        """
        키워드 출현 횟수 줄이기

        5-6회 → 2-3회로 감소
        """
        if not keyword or pd.isna(keyword):
            return text

        current_count = text.count(keyword)

        if current_count <= target_count:
            return text

        # 초과된 키워드를 대명사나 다른 표현으로 교체
        remove_count = current_count - target_count

        # 키워드를 찾아서 일부만 제거
        lines = text.split('\n')
        removed = 0

        for i, line in enumerate(lines):
            if removed >= remove_count:
                break

            if keyword in line:
                # 이 줄의 키워드를 대명사로 교체
                line_keyword_count = line.count(keyword)
                if line_keyword_count > 1:
                    # 두 번 이상 나오면 마지막 것만 제거
                    lines[i] = line.replace(keyword, '이거', line_keyword_count - 1)
                    removed += line_keyword_count - 1
                elif removed < remove_count and i > 0:
                    # 첫 줄 아니면 제거 가능
                    lines[i] = line.replace(keyword, '이거', 1)
                    removed += 1

        return '\n'.join(lines)

    def optimize_for_search(self, text: str, keyword: str) -> Dict:
        """
        검색 노출 최적화

        작업 순서:
        1. # 제목 삭제
        2. 키워드+조사 제거
        3. 키워드 출현 감소 (2-3회)
        4. 금칙어 치환
        5. AI 표현 제거
        """
        if pd.isna(text) or not text:
            return {
                'optimized_text': '',
                'original_length': 0,
                'optimized_length': 0,
                'keyword_count': 0,
                'changes': []
            }

        original_text = text
        original_length = len(text)
        all_changes = []

        # 1. # 제목 삭제
        text = self.remove_hashtag_title(text)
        all_changes.append('✅ # 제목 삭제')

        # 2. 키워드+조사 제거
        before_particle = text.count(keyword)
        text = self.remove_keyword_particles(text, keyword)
        after_particle = text.count(keyword)
        all_changes.append(f'✅ 키워드+조사 제거 ({before_particle}회)')

        # 3. 키워드 출현 감소 (2-3회 목표)
        text = self.reduce_keyword_frequency(text, keyword, target_count=2)
        final_count = text.count(keyword)
        all_changes.append(f'✅ 키워드 출현 감소 → {final_count}회')

        # 4. 금칙어 치환
        text, forbidden_changes = self.replace_forbidden_words(text)
        if forbidden_changes:
            all_changes.append(f'✅ 금칙어 {len(forbidden_changes)}개 치환')

        # 5. AI 패턴 다양화
        text, ai_changes = self.diversify_ai_patterns(text)
        if ai_changes:
            all_changes.append(f'✅ AI 표현 {len(ai_changes)}개 수정')

        # 6. 자연스러운 변형
        text = self.add_natural_variations(text)

        return {
            'optimized_text': text,
            'original_length': original_length,
            'optimized_length': len(text),
            'keyword_count': final_count,
            'changes': all_changes,
            'length_diff': len(text) - original_length
        }

    def process_excel(self, input_file: str, output_file: str = None) -> str:
        """
        엑셀 파일 일괄 처리
        """
        if output_file is None:
            output_file = input_file.replace('.xlsx', '_검색최적화.xlsx')

        # 엑셀 읽기
        df = pd.read_excel(input_file)

        # 새 컬럼 추가
        if '최적화_원고' not in df.columns:
            df['최적화_원고'] = ''
        if '키워드_출현' not in df.columns:
            df['키워드_출현'] = 0
        if '변경사항' not in df.columns:
            df['변경사항'] = ''

        # 각 행 처리
        for idx, row in df.iterrows():
            keyword = row.get('키워드', '')
            text = row.get('원고', '')

            if pd.isna(text) or not text:
                continue

            # 최적화
            result = self.optimize_for_search(text, keyword)

            # 결과 저장
            df.at[idx, '최적화_원고'] = result['optimized_text']
            df.at[idx, '키워드_출현'] = result['keyword_count']
            df.at[idx, '변경사항'] = '\n'.join(result['changes'])

        # 저장
        df.to_excel(output_file, index=False)
        return output_file
