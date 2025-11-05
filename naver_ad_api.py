"""
네이버 검색광고 API 연동 모듈
키워드 도구 API를 사용하여 키워드 경쟁력 데이터 수집
"""
import os
import hashlib
import hmac
import base64
import requests
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class NaverAdAPI:
    """네이버 검색광고 API 클라이언트"""

    def __init__(self):
        self.access_license = os.getenv('NAVER_API_ACCESS_LICENSE')
        self.secret_key = os.getenv('NAVER_API_SECRET_KEY')
        self.customer_id = os.getenv('NAVER_API_CUSTOMER_ID', '')

        self.base_url = 'https://api.naver.com'

        if not self.access_license or not self.secret_key:
            raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

    def _generate_signature(self, timestamp: str, method: str, uri: str) -> str:
        """API 요청 시그니처 생성"""
        message = f"{timestamp}.{method}.{uri}"

        # HMAC-SHA256 해싱
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # Base64 인코딩
        return base64.b64encode(signature).decode('utf-8')

    def _get_headers(self, method: str, uri: str) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, uri)

        headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Timestamp': timestamp,
            'X-API-KEY': self.access_license,
            'X-Customer': self.customer_id,
            'X-Signature': signature
        }

        return headers

    def get_keyword_ideas(
        self,
        keywords: List[str],
        show_detail: int = 1
    ) -> Optional[Dict]:
        """
        연관 키워드 조회 (키워드 도구)

        Args:
            keywords: 조회할 키워드 리스트 (최대 5개)
            show_detail: 상세 정보 표시 (1: 표시, 0: 비표시)

        Returns:
            키워드 정보 딕셔너리
        """
        uri = '/keywordstool'
        url = f"{self.base_url}{uri}"

        # 최대 5개 제한
        keywords = keywords[:5]

        payload = {
            "hintKeywords": keywords,
            "showDetail": show_detail
        }

        try:
            headers = self._get_headers('GET', uri)
            response = requests.get(
                url,
                headers=headers,
                params=payload,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API 오류: {response.status_code}")
                print(f"   응답: {response.text}")
                return None

        except Exception as e:
            print(f"❌ API 요청 실패: {e}")
            return None

    def analyze_keyword_competition(
        self,
        keyword: str
    ) -> Optional[Dict]:
        """
        키워드 경쟁력 분석

        Args:
            keyword: 분석할 키워드

        Returns:
            경쟁력 분석 결과
        """
        result = self.get_keyword_ideas([keyword])

        if not result or 'keywordList' not in result:
            return None

        # 첫 번째 키워드 데이터 추출
        keyword_data = result['keywordList'][0] if result['keywordList'] else None

        if not keyword_data:
            return None

        # 경쟁력 분석
        analysis = {
            'keyword': keyword_data.get('relKeyword', keyword),
            'monthly_search_pc': keyword_data.get('monthlyPcQcCnt', 0),
            'monthly_search_mobile': keyword_data.get('monthlyMobileQcCnt', 0),
            'monthly_avg_click_pc': keyword_data.get('monthlyAvePcClkCnt', 0),
            'monthly_avg_click_mobile': keyword_data.get('monthlyAveMobileClkCnt', 0),
            'monthly_avg_ctr_pc': keyword_data.get('monthlyAvePcCtr', 0),
            'monthly_avg_ctr_mobile': keyword_data.get('monthlyAveMobileCtr', 0),
            'competition': keyword_data.get('compIdx', '낮음'),  # 높음/중간/낮음
            'pl_avr_depth': keyword_data.get('plAvgDepth', 0),  # 평균 노출 광고수
        }

        # 총 검색수
        total_search = analysis['monthly_search_pc'] + analysis['monthly_search_mobile']
        analysis['total_monthly_search'] = total_search

        # 경쟁력 점수 계산 (0-100)
        competition_score = self._calculate_competition_score(analysis)
        analysis['competition_score'] = competition_score

        # 추천 여부
        analysis['recommended'] = self._is_keyword_recommended(analysis)

        return analysis

    def _calculate_competition_score(self, data: Dict) -> int:
        """
        키워드 경쟁력 점수 계산 (0-100)
        높을수록 경쟁이 치열함
        """
        score = 0

        # 1. 검색량 (30점)
        total_search = data['total_monthly_search']
        if total_search >= 10000:
            score += 30
        elif total_search >= 5000:
            score += 25
        elif total_search >= 1000:
            score += 20
        elif total_search >= 100:
            score += 10
        else:
            score += 5

        # 2. 경쟁정도 (40점)
        competition = data['competition']
        if competition == '높음':
            score += 40
        elif competition == '중간':
            score += 25
        else:
            score += 10

        # 3. 평균 노출 광고수 (30점)
        depth = data['pl_avr_depth']
        if depth >= 10:
            score += 30
        elif depth >= 7:
            score += 25
        elif depth >= 5:
            score += 20
        elif depth >= 3:
            score += 15
        else:
            score += 5

        return min(score, 100)

    def _is_keyword_recommended(self, data: Dict) -> bool:
        """
        키워드 추천 여부 판단
        검색량은 적당하고 경쟁은 낮은 키워드가 좋음
        """
        total_search = data['total_monthly_search']
        competition = data['competition']
        score = data['competition_score']

        # 추천 조건: 검색량 100 이상, 경쟁 낮음~중간, 점수 60 이하
        if total_search >= 100 and competition in ['낮음', '중간'] and score <= 60:
            return True

        return False

    def analyze_multiple_keywords(
        self,
        keywords: List[str]
    ) -> List[Dict]:
        """
        여러 키워드 일괄 분석

        Args:
            keywords: 키워드 리스트

        Returns:
            분석 결과 리스트
        """
        results = []

        # 5개씩 나눠서 요청
        for i in range(0, len(keywords), 5):
            batch = keywords[i:i+5]

            for keyword in batch:
                analysis = self.analyze_keyword_competition(keyword)
                if analysis:
                    results.append(analysis)

                # API 요청 제한 고려 (0.2초 대기)
                time.sleep(0.2)

        # 경쟁력 점수 기준 정렬 (낮은 순)
        results.sort(key=lambda x: x['competition_score'])

        return results

    def get_keyword_suggestions(
        self,
        seed_keyword: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        키워드 기반 추천 키워드 조회

        Args:
            seed_keyword: 기준 키워드
            max_results: 최대 결과 수

        Returns:
            추천 키워드 리스트
        """
        result = self.get_keyword_ideas([seed_keyword])

        if not result or 'keywordList' not in result:
            return []

        suggestions = []

        for kw_data in result['keywordList'][:max_results]:
            keyword = kw_data.get('relKeyword', '')
            if not keyword:
                continue

            suggestion = {
                'keyword': keyword,
                'monthly_search_pc': kw_data.get('monthlyPcQcCnt', 0),
                'monthly_search_mobile': kw_data.get('monthlyMobileQcCnt', 0),
                'competition': kw_data.get('compIdx', '낮음'),
                'total_monthly_search': (
                    kw_data.get('monthlyPcQcCnt', 0) +
                    kw_data.get('monthlyMobileQcCnt', 0)
                )
            }

            suggestions.append(suggestion)

        return suggestions


# 사용 예시
def main():
    """테스트 함수"""
    try:
        api = NaverAdAPI()

        # 1. 단일 키워드 분석
        print("=" * 60)
        print("📊 키워드 경쟁력 분석: '메디큐브'")
        print("=" * 60)

        result = api.analyze_keyword_competition("메디큐브")
        if result:
            print(f"\n키워드: {result['keyword']}")
            print(f"월간 총 검색수: {result['total_monthly_search']:,}")
            print(f"  - PC: {result['monthly_search_pc']:,}")
            print(f"  - 모바일: {result['monthly_search_mobile']:,}")
            print(f"경쟁정도: {result['competition']}")
            print(f"경쟁력 점수: {result['competition_score']}/100")
            print(f"평균 노출 광고수: {result['pl_avr_depth']}")
            print(f"추천 여부: {'✅ 추천' if result['recommended'] else '❌ 비추천'}")

        # 2. 연관 키워드 추천
        print("\n" + "=" * 60)
        print("🔍 연관 키워드 추천")
        print("=" * 60)

        suggestions = api.get_keyword_suggestions("메디큐브", max_results=5)
        for i, sugg in enumerate(suggestions, 1):
            print(f"\n{i}. {sugg['keyword']}")
            print(f"   검색수: {sugg['total_monthly_search']:,} | 경쟁: {sugg['competition']}")

    except Exception as e:
        print(f"❌ 오류: {e}")


if __name__ == "__main__":
    main()
