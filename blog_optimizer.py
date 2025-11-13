"""
블로그 원고 자동 최적화 시스템
- 금칙어 자동 치환
- SEO 최적화 (키워드 반복, 해시태그 등)
- AI 느낌 제거 (문장 패턴 다양화)
"""

import re
import random
from typing import Dict, List, Tuple
import pandas as pd


class BlogOptimizer:
    def __init__(self, forbidden_words_file='금칙어 수정사항 모음.txt'):
        """초기화"""
        self.forbidden_words = self._load_forbidden_words(forbidden_words_file)

        # AI 느낌 나는 표현들 (다양화 필요)
        self.ai_patterns = {
            '정말 고민이 많습니다': [
                '정말 고민되네요',
                '어떻게 해야 할지 모르겠어요',
                '생각이 많아지네요'
            ],
            '절로 나오': [
                '자연스럽게 나오',
                '저도 모르게 나오',
                '무심코 나오'
            ],
            '고생하고 있는': [
                '힘들어하는',
                '어려움을 겪는',
                '불편함을 느끼는'
            ],
            '이렇게 글을 올려봅니다': [
                '여쭤보고 싶어서요',
                '궁금해서 글 남겨요',
                '조언 구하러 왔어요'
            ],
            '솔직히': [
                '사실',
                '실제로',
                '있는 그대로 말하면'
            ],
            '정말': [
                '진짜',
                '확실히',
                '분명히'
            ],
            '너무': [
                '엄청',
                '많이',
                '굉장히'
            ]
        }

    def _load_forbidden_words(self, filepath: str) -> Dict[str, str]:
        """금칙어 파일 로드"""
        forbidden_dict = {}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            current_forbidden = None
            for line in lines:
                line = line.strip()
                if not line:
                    current_forbidden = None
                    continue

                # 금칙어와 대체어 구분
                if current_forbidden is None:
                    current_forbidden = line
                else:
                    replacement = line

                    # (삭제), (삭제처리) 등은 빈 문자열로
                    if '삭제' in replacement:
                        replacement = ''
                    # 괄호 안의 설명 제거
                    elif '(' in replacement:
                        replacement = re.sub(r'\(.*?\)', '', replacement).strip()

                    # "/" 또는 "," 로 구분된 여러 대체어 중 하나 랜덤 선택
                    if ('/' in replacement or ',' in replacement) and replacement:
                        # "/" 또는 ","로 구분
                        separators = ['/', ',']
                        for sep in separators:
                            if sep in replacement:
                                options = [opt.strip() for opt in replacement.split(sep)]
                                options = [opt for opt in options if opt and len(opt) < 10]  # 빈 문자열 및 너무 긴 옵션 제거
                                if options:
                                    replacement = random.choice(options)
                                break

                    # 너무 긴 대체어는 무시 (설명문으로 판단)
                    if len(replacement) > 15:
                        replacement = ''

                    forbidden_dict[current_forbidden] = replacement
                    current_forbidden = None

        except Exception as e:
            print(f"금칙어 파일 로드 실패: {e}")

        return forbidden_dict

    def replace_forbidden_words(self, text: str) -> Tuple[str, List[str]]:
        """금칙어 치환"""
        replaced_words = []

        for forbidden, replacement in self.forbidden_words.items():
            if forbidden in text:
                text = text.replace(forbidden, replacement)
                replaced_words.append(f"{forbidden} → {replacement if replacement else '(삭제)'}")

        return text, replaced_words

    def diversify_ai_patterns(self, text: str) -> Tuple[str, List[str]]:
        """AI 느낌 나는 패턴 다양화"""
        diversified = []

        for pattern, alternatives in self.ai_patterns.items():
            if pattern in text:
                replacement = random.choice(alternatives)
                text = text.replace(pattern, replacement, 1)  # 첫 번째만 교체
                diversified.append(f"{pattern} → {replacement}")

        return text, diversified

    def optimize_keyword_density(self, text: str, keyword: str, target_count: int = 5) -> Tuple[str, int]:
        """키워드 밀도 최적화"""
        if not keyword or pd.isna(keyword):
            return text, 0

        # 현재 키워드 출현 횟수
        current_count = text.count(keyword)

        if current_count >= target_count:
            return text, current_count

        # 키워드를 자연스럽게 추가할 수 있는 위치 찾기
        # 1) "이런", "이거", "그거", "그런" 등을 키워드로 교체
        pronouns = ['이런', '이거', '그거', '그런', '그게', '이게']
        added = 0

        for pronoun in pronouns:
            if added >= (target_count - current_count):
                break
            if pronoun in text:
                # 첫 번째 발견된 대명사만 교체
                text = text.replace(pronoun, keyword, 1)
                added += 1

        final_count = text.count(keyword)
        return text, final_count

    def add_natural_variations(self, text: str) -> str:
        """자연스러운 문장 변형 추가"""
        # 동일한 문장 패턴 방지
        text = re.sub(r'(정말|너무|굉장히)\s+(정말|너무|굉장히)', r'\1', text)

        # "~하더라고요" 과다 사용 방지
        count = text.count('하더라고요')
        if count > 2:
            alternatives = ['하더군요', '했어요', '했습니다', '했죠']
            for i in range(count - 2):
                text = text.replace('하더라고요', random.choice(alternatives), 1)

        # "~네요" 과다 사용 방지
        count = text.count('네요')
        if count > 3:
            alternatives = ['어요', '습니다', '죠']
            for i in range(count - 3):
                text = text.replace('네요', random.choice(alternatives), 1)

        return text

    def generate_title(self, keyword: str, original_text: str) -> str:
        """SEO 최적화 제목 생성 (15-40자 권장)"""
        if not keyword or pd.isna(keyword):
            return ''

        # 제목 템플릿 (상품 판매용)
        templates = [
            f"{keyword} 추천 정보 (후기 모음)",
            f"{keyword} 어떤 게 좋을까요?",
            f"{keyword} 정보 공유",
            f"{keyword} 사용 경험담",
            f"{keyword} 이거 어떤가요?",
            f"{keyword} 관련 궁금한 점",
            f"{keyword} 정보 찾아봤어요",
        ]

        # 랜덤으로 하나 선택
        title = random.choice(templates)

        # 15-40자 범위 확인
        if len(title) < 15:
            title += " (솔직 후기)"
        elif len(title) > 40:
            title = title[:40]

        return title

    def generate_hashtags(self, keyword: str, brand: str) -> List[str]:
        """SEO 최적화 해시태그 생성 (8-10개 권장)"""
        hashtags = []

        if not pd.isna(keyword):
            # 메인 키워드
            hashtags.append(keyword)

            # 키워드 조각 분리
            keyword_parts = keyword.split()
            hashtags.extend(keyword_parts)

        if not pd.isna(brand):
            hashtags.append(brand)

        # 관절/건강 관련 일반 해시태그
        general_tags = [
            '건강정보',
            '건강관리',
            '일상',
            '후기',
            '정보공유',
            '추천',
            '관절건강',
            '건강식품'
        ]

        # 중복 제거하고 8-10개 맞추기
        hashtags = list(dict.fromkeys(hashtags))  # 중복 제거

        # 부족하면 일반 태그 추가
        while len(hashtags) < 8:
            tag = random.choice([t for t in general_tags if t not in hashtags])
            hashtags.append(tag)

        # 너무 많으면 자르기
        hashtags = hashtags[:10]

        return hashtags

    def optimize_text(self, text: str, keyword: str = '', brand: str = '', title: str = '') -> Dict:
        """텍스트 전체 최적화"""
        if pd.isna(text) or not text:
            return {
                'optimized_text': '',
                'optimized_title': '',
                'changes': [],
                'keyword_count': 0,
                'hashtags': []
            }

        original_text = text
        changes = []

        # 1. 금칙어 치환
        text, forbidden_changes = self.replace_forbidden_words(text)
        changes.extend(forbidden_changes)

        # 2. AI 패턴 다양화
        text, ai_changes = self.diversify_ai_patterns(text)
        changes.extend(ai_changes)

        # 3. 키워드 밀도 최적화
        text, keyword_count = self.optimize_keyword_density(text, keyword)
        if keyword_count > 0:
            changes.append(f"키워드 '{keyword}' 출현: {keyword_count}회")

        # 4. 자연스러운 변형
        text = self.add_natural_variations(text)

        # 5. 해시태그 생성
        hashtags = self.generate_hashtags(keyword, brand)

        # 6. 제목 생성 (없는 경우)
        if pd.isna(title) or not title:
            title = self.generate_title(keyword, text)

        return {
            'optimized_text': text,
            'optimized_title': title,
            'original_length': len(original_text),
            'optimized_length': len(text),
            'changes': changes,
            'keyword_count': keyword_count,
            'hashtags': hashtags
        }

    def optimize_excel(self, input_file: str, output_file: str = None) -> Dict:
        """엑셀 파일 전체 최적화"""
        if output_file is None:
            output_file = input_file.replace('.xlsx', '_최적화.xlsx')

        # 엑셀 읽기
        df = pd.read_excel(input_file)

        results = []

        # 각 행 최적화
        for idx, row in df.iterrows():
            keyword = row.get('키워드', '')
            brand = row.get('브랜드', '')
            original_text = row.get('원고', '')
            title = row.get('제목', '')

            # 최적화 실행
            result = self.optimize_text(original_text, keyword, brand, title)

            # 결과 저장
            df.at[idx, '원고'] = result['optimized_text']

            # 제목 추가/업데이트
            if result['optimized_title']:
                df.at[idx, '제목'] = result['optimized_title']

            # 해시태그 추가 (새 컬럼)
            df.at[idx, '추천_해시태그'] = ' #'.join([''] + result['hashtags'])

            # 변경 사항 기록
            df.at[idx, '최적화_변경사항'] = '\n'.join(result['changes'])

            results.append({
                'row': idx + 1,
                'keyword': keyword,
                'keyword_count': result['keyword_count'],
                'changes_count': len(result['changes']),
                'hashtags_count': len(result['hashtags'])
            })

        # 엑셀 저장
        df.to_excel(output_file, index=False)

        return {
            'input_file': input_file,
            'output_file': output_file,
            'total_rows': len(df),
            'results': results
        }


def main():
    """메인 실행"""
    optimizer = BlogOptimizer()

    # 엑셀 최적화
    result = optimizer.optimize_excel('작업 의뢰용 데이터.xlsx')

    print("\n" + "=" * 80)
    print("🎉 블로그 원고 최적화 완료!")
    print("=" * 80)
    print(f"\n📂 입력 파일: {result['input_file']}")
    print(f"📁 출력 파일: {result['output_file']}")
    print(f"📊 처리된 행: {result['total_rows']}개")
    print("\n" + "=" * 80)
    print("각 행별 최적화 결과:")
    print("=" * 80)

    for r in result['results']:
        print(f"\n[{r['row']}행] 키워드: {r['keyword']}")
        print(f"  ✅ 키워드 출현: {r['keyword_count']}회")
        print(f"  ✅ 변경 사항: {r['changes_count']}건")
        print(f"  ✅ 해시태그: {r['hashtags_count']}개")

    print("\n" + "=" * 80)
    print("✅ 최적화 완료!")
    print("📝 엑셀 파일을 열어서 다음 컬럼을 확인하세요:")
    print("   - 원고: 최적화된 원고")
    print("   - 제목: SEO 최적화 제목")
    print("   - 추천_해시태그: 8-10개의 추천 해시태그")
    print("   - 최적화_변경사항: 금칙어 치환 등 변경 내역")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
