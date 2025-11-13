"""
TXT 파일 기반 블로그 원고 최적화 시스템

사용법:
1. 대화형 모드: python3 optimize_txt.py
2. 직접 지정: python3 optimize_txt.py --input 원고.txt --output 최적화_원고.txt
3. 폴더 일괄 처리: python3 optimize_txt.py --folder ./원고폴더
"""

import os
import sys
import argparse
from pathlib import Path
from advanced_seo_optimizer import AdvancedSEOOptimizer


class TxtOptimizer:
    """TXT 파일 최적화 시스템"""

    def __init__(self):
        self.optimizer = AdvancedSEOOptimizer()

    def optimize_single_file(
        self,
        input_file: str,
        output_file: str = None,
        keyword: str = None,
        brand: str = "",
        target_char_count: int = 2000,
        target_whole_keyword: int = 6,
        target_subkeyword_count: int = 18,
        target_keyword_start: int = 4
    ):
        """
        단일 txt 파일 최적화

        Args:
            input_file: 입력 txt 파일 경로
            output_file: 출력 txt 파일 경로 (None이면 자동 생성)
            keyword: 통키워드 (None이면 자동 추출 시도)
            brand: 브랜드명
            target_char_count: 목표 글자수
            target_whole_keyword: 목표 통키워드 반복수
            target_subkeyword_count: 목표 서브키워드 개수
            target_keyword_start: 키워드 시작 문장 수
        """
        print(f"\n{'='*80}")
        print(f"📝 파일 최적화 시작: {input_file}")
        print(f"{'='*80}\n")

        # 입력 파일 읽기
        if not os.path.exists(input_file):
            print(f"❌ 오류: 파일을 찾을 수 없습니다 - {input_file}")
            return None

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                original_text = f.read()
        except Exception as e:
            print(f"❌ 파일 읽기 오류: {e}")
            return None

        if not original_text.strip():
            print(f"❌ 오류: 파일이 비어있습니다")
            return None

        # 키워드 자동 추출 (제목에서)
        if keyword is None:
            # 첫 번째 줄이나 # 제목에서 키워드 추출 시도
            lines = original_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('#'):
                    # "# 팔꿈치 쿠션 보호대 관련해서..." → "팔꿈치 쿠션 보호대"
                    line = line.lstrip('#').strip()
                    # "관련", "에 대해" 등 제거
                    for suffix in ['관련해서', '에 대해', '관련', '사용', '후기', '정보']:
                        if suffix in line:
                            line = line.split(suffix)[0].strip()
                            break
                    keyword = line
                    break

            if not keyword:
                print("⚠️ 키워드를 자동 추출하지 못했습니다. 수동으로 입력해주세요.")
                keyword = input("키워드 입력: ").strip()

        print(f"🔑 키워드: {keyword}")
        print(f"📏 현재 글자수: {len(original_text)}자")
        print(f"🎯 목표 글자수: {target_char_count}자")

        # 최적화 실행
        try:
            result = self.optimizer.optimize_advanced(
                text=original_text,
                keyword=keyword,
                brand=brand,
                title="",
                target_char_count=target_char_count,
                target_whole_keyword=target_whole_keyword,
                target_subkeyword_count=target_subkeyword_count,
                target_keyword_start=target_keyword_start
            )

            # 결과 출력
            final_status = result['final_status']
            c_rank = result['c_rank_check']

            print(f"\n{'='*80}")
            print("✅ 최적화 완료!")
            print(f"{'='*80}")
            print(f"📊 최종 글자수: {final_status['char_count']}자 "
                  f"(+{final_status['char_count'] - len(original_text)}자)")
            print(f"🔑 통키워드 출현: {final_status['whole_keyword_count']}회")
            print(f"🧩 조각키워드: {final_status['piece_counts']}")
            print(f"🏷️ 서브키워드: {final_status['subkeyword_count']}개")
            print(f"📌 키워드 시작 문장: {final_status['keyword_start_sentences']}개")
            print(f"📈 C랭크: {c_rank['rank']}등급 ({c_rank['score']}점)")

            # 출력 파일 경로 결정
            if output_file is None:
                base_name = os.path.splitext(input_file)[0]
                output_file = f"{base_name}_최적화.txt"

            # 결과 저장
            self._save_result(output_file, result, keyword)

            print(f"\n💾 저장 완료: {output_file}")
            print(f"{'='*80}\n")

            return result

        except Exception as e:
            print(f"❌ 최적화 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _save_result(self, output_file: str, result: dict, keyword: str):
        """결과를 txt 파일로 저장"""
        final_status = result['final_status']
        c_rank = result['c_rank_check']

        # 파일 작성
        with open(output_file, 'w', encoding='utf-8') as f:
            # 헤더 정보
            f.write("=" * 80 + "\n")
            f.write("블로그 원고 최적화 결과\n")
            f.write("=" * 80 + "\n\n")

            # SEO 정보
            f.write("📊 SEO 분석\n")
            f.write("-" * 80 + "\n")
            f.write(f"키워드: {keyword}\n")
            f.write(f"글자수: {final_status['char_count']}자\n")
            f.write(f"통키워드 출현: {final_status['whole_keyword_count']}회\n")
            f.write(f"조각키워드: {final_status['piece_counts']}\n")
            f.write(f"서브키워드: {final_status['subkeyword_count']}개\n")
            f.write(f"키워드 시작 문장: {final_status['keyword_start_sentences']}개\n")
            f.write(f"C랭크 점수: {c_rank['score']}점 ({c_rank['rank']}등급)\n")
            f.write("\n")

            # 해시태그
            f.write("🏷️ 추천 해시태그\n")
            f.write("-" * 80 + "\n")
            f.write(" #".join([''] + result['hashtags']) + "\n\n")

            # C랭크 제안사항
            f.write("💡 C랭크 제안사항\n")
            f.write("-" * 80 + "\n")
            for issue in c_rank['issues']:
                f.write(f"{issue}\n")
            f.write("\n")

            # 제목
            if result.get('optimized_title'):
                f.write("📌 제목\n")
                f.write("-" * 80 + "\n")
                f.write(f"{result['optimized_title']}\n\n")

            # 본문
            f.write("=" * 80 + "\n")
            f.write("📝 최적화된 원고\n")
            f.write("=" * 80 + "\n\n")
            f.write(result['optimized_text'])

    def optimize_folder(self, folder_path: str, output_folder: str = None):
        """
        폴더 내 모든 txt 파일 일괄 처리

        Args:
            folder_path: 입력 폴더 경로
            output_folder: 출력 폴더 경로 (None이면 입력 폴더 내에 '최적화' 폴더 생성)
        """
        if not os.path.exists(folder_path):
            print(f"❌ 오류: 폴더를 찾을 수 없습니다 - {folder_path}")
            return

        # txt 파일 찾기
        txt_files = list(Path(folder_path).glob("*.txt"))
        if not txt_files:
            print(f"❌ 오류: txt 파일이 없습니다 - {folder_path}")
            return

        print(f"\n{'='*80}")
        print(f"📂 폴더 일괄 처리: {folder_path}")
        print(f"📝 총 {len(txt_files)}개 파일 발견")
        print(f"{'='*80}\n")

        # 출력 폴더 생성
        if output_folder is None:
            output_folder = os.path.join(folder_path, "최적화")
        os.makedirs(output_folder, exist_ok=True)

        # 각 파일 처리
        success_count = 0
        for i, txt_file in enumerate(txt_files, 1):
            print(f"\n[{i}/{len(txt_files)}] 처리 중: {txt_file.name}")

            output_file = os.path.join(output_folder, f"{txt_file.stem}_최적화.txt")

            result = self.optimize_single_file(
                input_file=str(txt_file),
                output_file=output_file
            )

            if result:
                success_count += 1

        print(f"\n{'='*80}")
        print(f"✅ 일괄 처리 완료!")
        print(f"{'='*80}")
        print(f"성공: {success_count}개")
        print(f"실패: {len(txt_files) - success_count}개")
        print(f"출력 폴더: {output_folder}")
        print(f"{'='*80}\n")

    def interactive_mode(self):
        """대화형 모드"""
        print("\n" + "=" * 80)
        print("🎯 블로그 원고 최적화 시스템 (TXT 모드)")
        print("=" * 80 + "\n")

        # 모드 선택
        print("모드를 선택하세요:")
        print("1. 단일 파일 최적화")
        print("2. 폴더 일괄 처리")
        print("3. 종료")

        choice = input("\n선택 (1-3): ").strip()

        if choice == '1':
            # 단일 파일 모드
            input_file = input("\n입력 파일 경로: ").strip()
            output_file = input("출력 파일 경로 (Enter=자동): ").strip()
            keyword = input("키워드 (Enter=자동 추출): ").strip()
            brand = input("브랜드명 (선택사항): ").strip()

            if not output_file:
                output_file = None
            if not keyword:
                keyword = None

            self.optimize_single_file(
                input_file=input_file,
                output_file=output_file,
                keyword=keyword,
                brand=brand
            )

        elif choice == '2':
            # 폴더 일괄 처리 모드
            folder_path = input("\n입력 폴더 경로: ").strip()
            output_folder = input("출력 폴더 경로 (Enter=자동): ").strip()

            if not output_folder:
                output_folder = None

            self.optimize_folder(
                folder_path=folder_path,
                output_folder=output_folder
            )

        elif choice == '3':
            print("종료합니다.")
            return

        else:
            print("잘못된 선택입니다.")


def main():
    """메인 실행"""
    parser = argparse.ArgumentParser(
        description='TXT 파일 기반 블로그 원고 최적화',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  1. 대화형 모드:
     python3 optimize_txt.py

  2. 단일 파일 최적화:
     python3 optimize_txt.py --input 원고.txt --output 최적화_원고.txt

  3. 키워드 지정:
     python3 optimize_txt.py --input 원고.txt --keyword "팔꿈치 쿠션 보호대"

  4. 폴더 일괄 처리:
     python3 optimize_txt.py --folder ./원고폴더

  5. 목표 글자수 지정:
     python3 optimize_txt.py --input 원고.txt --target-chars 2500
        """
    )

    parser.add_argument('--input', '-i', help='입력 txt 파일 경로')
    parser.add_argument('--output', '-o', help='출력 txt 파일 경로')
    parser.add_argument('--folder', '-f', help='폴더 일괄 처리')
    parser.add_argument('--keyword', '-k', help='통키워드')
    parser.add_argument('--brand', '-b', default='', help='브랜드명')
    parser.add_argument('--target-chars', '-t', type=int, default=2000, help='목표 글자수 (기본: 2000)')
    parser.add_argument('--target-keyword', type=int, default=6, help='목표 통키워드 반복수 (기본: 6)')

    args = parser.parse_args()

    optimizer = TxtOptimizer()

    # 폴더 모드
    if args.folder:
        optimizer.optimize_folder(args.folder)
    # 파일 모드
    elif args.input:
        optimizer.optimize_single_file(
            input_file=args.input,
            output_file=args.output,
            keyword=args.keyword,
            brand=args.brand,
            target_char_count=args.target_chars,
            target_whole_keyword=args.target_keyword
        )
    # 대화형 모드
    else:
        optimizer.interactive_mode()


if __name__ == '__main__':
    main()
