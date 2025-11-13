#!/usr/bin/env python3
"""
금칙어 리스트 로더 (간단 버전)

Excel 파일에서 금칙어와 대체어를 로드
"""

from typing import Dict, List
import openpyxl


class ForbiddenWordsLoader:
    """금칙어 리스트 로더"""

    def __init__(self, excel_file: str = '금칙어 리스트.xlsx'):
        """
        초기화

        Args:
            excel_file: 금칙어 리스트 Excel 파일
        """
        self.excel_file = excel_file
        self.replacements = {}

        try:
            self._load_from_excel()
        except Exception as e:
            print(f"⚠️ 금칙어 파일 로드 실패: {e}")
            self._load_default()

    def _load_from_excel(self):
        """Excel에서 금칙어 로드"""
        wb = openpyxl.load_workbook(self.excel_file)
        ws = wb.active

        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue

            # A열: 번호 (스킵)
            # B열: 금칙어
            # C열 이후: 대체어들
            forbidden = row[1]
            alternatives = [cell for cell in row[2:] if cell]

            if forbidden and alternatives:
                self.replacements[forbidden] = alternatives

    def _load_default(self):
        """기본 금칙어 리스트"""
        self.replacements = {
            "네요": ["어요", "해요"],
            "가격": ["경비", "금액"],
            "광고": ["소개", "홍보"],
            "구매": ["선택", "구입"],
            "병원": ["병의원", "클리닉", "센터"],
            "진단": ["확인", "검사"],
            "효과": ["도움", "개선"],
            "약효": ["효능", "도움"],
            "상담": ["문의", "얘기", "안내"],
            "시술": ["관리", "치료"],
            "의사": ["전문의", "의료진"],
            "환자": ["분", "사람"],
            "판매": ["제공", "판매"],
            "투자": ["지출", "사용"],
            "후회": ["아쉬움", "안타까움"],
            "보험": ["보장", "혜택"],
            "재발": ["다시", "또"],
            "대출": ["금융", "자금"],
            "비용": ["경비", "금액"],
            "의문": ["궁금", "의심"],
            "의심": ["궁금", "의문"],
            "산부인과": ["병원", "부인과", "병의원"],
            "부작용": ["안 좋은 반응", "부정적인 면"],
            "홍보성": ["소개", "광고"],
            "의구심": ["궁금", "의심"],
            "증상": ["증세", "이런 느낌", "몸 상태"],
        }

    def get_replacements(self) -> Dict[str, List[str]]:
        """
        금칙어 대체 딕셔너리 반환

        Returns:
            {금칙어: [대체어들]}
        """
        return self.replacements


def test_loader():
    """테스트"""

    loader = ForbiddenWordsLoader()

    replacements = loader.get_replacements()

    print("="*80)
    print("금칙어 리스트")
    print("="*80)

    for forbidden, alternatives in list(replacements.items())[:10]:
        print(f"\n{forbidden} →")
        for alt in alternatives:
            print(f"  - {alt}")

    print(f"\n\n총 {len(replacements)}개의 금칙어")


if __name__ == '__main__':
    test_loader()
