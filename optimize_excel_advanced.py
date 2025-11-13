"""
엑셀 파일 고급 SEO 최적화 실행 스크립트
"""

import pandas as pd
from advanced_seo_optimizer import AdvancedSEOOptimizer


def parse_seo_settings(row) -> dict:
    """엑셀에서 SEO 설정 파싱 (현재 상태)"""
    settings = {}

    # 글자수
    settings['current_char_count'] = row.get('글자수(공백포함)', 0)

    # 통키워드 반복수 파싱
    whole_keyword_str = str(row.get('통키워드 반복수', ''))
    if ':' in whole_keyword_str:
        parts = whole_keyword_str.split(':')
        if len(parts) == 2:
            try:
                settings['current_whole_keyword'] = int(parts[1].strip())
            except:
                settings['current_whole_keyword'] = 0
    else:
        settings['current_whole_keyword'] = 0

    # 조각키워드 반복수 파싱
    piece_keyword_str = str(row.get('조각키워드 반복수', ''))
    settings['current_piece_keywords'] = {}
    if piece_keyword_str and piece_keyword_str != '-' and piece_keyword_str != 'nan':
        lines = piece_keyword_str.split('\n')
        for line in lines:
            if ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    keyword = parts[0].strip()
                    try:
                        count = int(parts[1].strip())
                        settings['current_piece_keywords'][keyword] = count
                    except:
                        pass

    # 서브키워드 목록 수
    settings['current_subkeyword_count'] = row.get('서브키워드 목록 수', 0)
    if pd.isna(settings['current_subkeyword_count']):
        settings['current_subkeyword_count'] = 0

    return settings


def set_target_seo_goals(keyword: str, current_settings: dict) -> dict:
    """
    목표 SEO 기준 자동 설정

    네이버 C랭크 기준에 맞춘 합리적인 목표값 설정
    """
    goals = {}

    # 1. 목표 글자수: 2000-2500자 (C랭크 기준)
    goals['target_char_count'] = 2000

    # 2. 목표 통키워드: 5-7회 (자연스러운 범위)
    goals['target_whole_keyword'] = 6

    # 3. 목표 조각키워드: 통키워드의 1.5-2배
    if ' ' in keyword:
        pieces = keyword.split()
        goals['target_piece_keywords'] = {}
        for piece in pieces:
            # 첫 번째 조각은 더 많이, 나머지는 적게
            if piece == pieces[0]:
                goals['target_piece_keywords'][piece] = 12
            else:
                goals['target_piece_keywords'][piece] = 8
    else:
        goals['target_piece_keywords'] = {}

    # 4. 목표 서브키워드: 15-20개
    goals['target_subkeyword_count'] = 18

    # 5. 키워드로 시작하는 문장: 3-4개
    goals['target_keyword_start'] = 4

    return goals


def main():
    """메인 실행"""
    optimizer = AdvancedSEOOptimizer()

    # 엑셀 읽기
    input_file = '작업 의뢰용 데이터.xlsx'
    output_file = '작업 의뢰용 데이터_고급최적화.xlsx'

    df = pd.read_excel(input_file)

    results = []

    print("\n" + "=" * 100)
    print("고급 SEO 최적화 시작")
    print("=" * 100)

    for idx, row in df.iterrows():
        keyword = row.get('키워드', '')
        brand = row.get('브랜드', '')
        original_text = row.get('원고', '')
        title = row.get('제목', '')

        print(f"\n[{idx+1}/{len(df)}] {keyword} 최적화 중...")

        # 현재 SEO 설정 파싱
        current_settings = parse_seo_settings(row)

        # 목표 SEO 기준 설정
        goals = set_target_seo_goals(keyword, current_settings)

        print(f"  현재: 글자수 {current_settings['current_char_count']}자, "
              f"통키워드 {current_settings['current_whole_keyword']}회")
        print(f"  목표: 글자수 {goals['target_char_count']}자, "
              f"통키워드 {goals['target_whole_keyword']}회")

        # 고급 최적화 실행
        try:
            result = optimizer.optimize_advanced(
                text=original_text,
                keyword=keyword,
                brand=brand,
                title=title,
                target_char_count=goals['target_char_count'],
                target_whole_keyword=goals['target_whole_keyword'],
                target_piece_keywords=goals.get('target_piece_keywords'),
                target_subkeyword_count=goals['target_subkeyword_count'],
                target_keyword_start=goals['target_keyword_start']
            )

            # 결과 저장
            df.at[idx, '원고'] = result['optimized_text']

            # 제목
            if result['optimized_title']:
                df.at[idx, '제목'] = result['optimized_title']

            # 최적화 후 상태 업데이트
            final_status = result['final_status']

            df.at[idx, '글자수(공백포함)'] = final_status['char_count']

            # 통키워드 반복수
            df.at[idx, '통키워드 반복수'] = f"{keyword} : {final_status['whole_keyword_count']}"

            # 조각키워드 반복수
            piece_str = '\n'.join([f"{k} : {v}" for k, v in final_status['piece_counts'].items()])
            if not piece_str:
                piece_str = '-'
            df.at[idx, '조각키워드 반복수'] = piece_str

            # 서브키워드 목록 수
            df.at[idx, '서브키워드 목록 수'] = final_status['subkeyword_count']

            # 해시태그
            df.at[idx, '추천_해시태그'] = ' #'.join([''] + result['hashtags'])

            # C랭크 정보
            c_rank = result['c_rank_check']
            df.at[idx, 'C랭크_점수'] = c_rank.get('score', 0)
            df.at[idx, 'C랭크_등급'] = c_rank.get('rank', 'F')
            df.at[idx, 'C랭크_제안사항'] = '\n'.join(c_rank.get('issues', []))

            # 최적화 변경사항
            df.at[idx, '최적화_변경사항'] = '\n'.join(result['changes'])

            # 결과 기록
            results.append({
                'row': idx + 1,
                'keyword': keyword,
                'before_char': current_settings['current_char_count'],
                'after_char': final_status['char_count'],
                'before_whole_keyword': current_settings['current_whole_keyword'],
                'after_whole_keyword': final_status['whole_keyword_count'],
                'after_subkeyword': final_status['subkeyword_count'],
                'keyword_start_sentences': final_status['keyword_start_sentences'],
                'c_rank': c_rank.get('rank', 'F'),
                'c_score': c_rank.get('score', 0)
            })

            print(f"  ✅ 완료: 글자수 {final_status['char_count']}자, "
                  f"통키워드 {final_status['whole_keyword_count']}회, "
                  f"C랭크 {c_rank.get('rank', 'F')}등급")

        except Exception as e:
            print(f"  ❌ 오류: {e}")
            results.append({
                'row': idx + 1,
                'keyword': keyword,
                'error': str(e)
            })

    # 엑셀 저장
    df.to_excel(output_file, index=False)

    # 결과 요약
    print("\n" + "=" * 100)
    print("✅ 고급 최적화 완료!")
    print("=" * 100)
    print(f"\n📂 입력 파일: {input_file}")
    print(f"📁 출력 파일: {output_file}")
    print(f"📊 처리된 행: {len(df)}개")

    print("\n" + "=" * 100)
    print("최적화 결과 요약")
    print("=" * 100)

    for r in results:
        if 'error' in r:
            print(f"\n[{r['row']}행] {r['keyword']} - 오류: {r['error']}")
        else:
            print(f"\n[{r['row']}행] {r['keyword']}")
            print(f"  📝 글자수: {r['before_char']}자 → {r['after_char']}자 "
                  f"(+{r['after_char'] - r['before_char']}자)")
            print(f"  🔑 통키워드: {r['before_whole_keyword']}회 → {r['after_whole_keyword']}회")
            print(f"  🏷️ 서브키워드: {r['after_subkeyword']}개")
            print(f"  📌 키워드 시작 문장: {r['keyword_start_sentences']}개")
            print(f"  📈 C랭크: {r['c_rank']}등급 ({r['c_score']}점)")

    print("\n" + "=" * 100)
    print("📝 상세 내용은 엑셀 파일을 확인하세요!")
    print("=" * 100 + "\n")


if __name__ == '__main__':
    main()
