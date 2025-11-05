"""
네이버 블로그 크롤러 - 순수 데이터 수집 전용
분석 로직 없이 빠르게 raw 데이터만 수집
비동기 HTTP 요청으로 대량 크롤링 지원
"""
import re
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import json


class NaverBlogCrawler:
    """네이버 블로그 크롤러"""

    def __init__(self, max_posts: int = 100, timeout: int = 15):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36',
            'Referer': 'https://blog.naver.com/',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        self.timeout = timeout
        self.max_posts = max_posts

    async def crawl_blog(self, blog_id: str, save_to_file: bool = False) -> Dict:
        """
        블로그 전체 크롤링

        Args:
            blog_id: 네이버 블로그 ID
            save_to_file: JSON 파일로 저장 여부

        Returns:
            크롤링된 데이터 (딕셔너리)
        """
        print(f"🚀 [{blog_id}] 크롤링 시작...")

        # 1. 게시글 URL 수집
        post_urls = await self._collect_post_urls(blog_id)
        if not post_urls:
            print(f"❌ [{blog_id}] 게시글을 찾을 수 없습니다.")
            return None

        print(f"✅ [{blog_id}] {len(post_urls)}개 게시글 URL 수집 완료")

        # 2. 각 게시글 병렬 크롤링
        async with aiohttp.ClientSession(headers=self.headers) as session:
            tasks = [
                self._crawl_single_post(session, url, blog_id)
                for url in post_urls[:self.max_posts]
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        # 성공한 결과만 필터링
        posts = []
        for result in results:
            if result and not isinstance(result, Exception):
                posts.append(result)

        print(f"✅ [{blog_id}] {len(posts)}/{len(post_urls)} 게시글 크롤링 완료")

        # 3. 블로그 정보 수집
        blog_info = await self._get_blog_info(blog_id)

        # 4. 최종 결과
        result = {
            "blog_id": blog_id,
            "blog_info": blog_info,
            "total_posts": len(posts),
            "posts": posts,
            "crawled_at": datetime.now().isoformat()
        }

        # 5. 파일 저장
        if save_to_file:
            filename = f"{blog_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"💾 [{blog_id}] 데이터 저장 완료: {filename}")

        return result

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """비동기 HTTP 요청"""
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"⚠️ HTTP {response.status}: {url}")
                    return None
        except asyncio.TimeoutError:
            print(f"⏱️ Timeout: {url}")
            return None
        except Exception as e:
            print(f"❌ Error: {url} - {e}")
            return None

    async def _collect_post_urls(self, blog_id: str) -> List[str]:
        """게시글 URL 수집 (다중 폴백)"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            urls = []

            # 방법 1: RSS (가장 안정적)
            print(f"📡 [{blog_id}] RSS로 URL 수집 시도...")
            urls = await self._collect_from_rss(session, blog_id)
            if urls:
                return urls

            # 방법 2: PC 메인 → iframe
            print(f"📡 [{blog_id}] PC 메인페이지로 URL 수집 시도...")
            urls = await self._collect_from_main(session, blog_id)
            if urls:
                return urls

            # 방법 3: PostList API
            print(f"📡 [{blog_id}] PostList API로 URL 수집 시도...")
            urls = await self._collect_from_postlist(session, blog_id)
            if urls:
                return urls

            # 방법 4: 모바일 페이지
            print(f"📡 [{blog_id}] 모바일 페이지로 URL 수집 시도...")
            urls = await self._collect_from_mobile(session, blog_id)

            return urls

    async def _collect_from_rss(self, session: aiohttp.ClientSession, blog_id: str) -> List[str]:
        """RSS에서 URL 수집"""
        try:
            rss_url = f"https://rss.blog.naver.com/{blog_id}.xml"
            html = await self._fetch(session, rss_url)
            if not html:
                return []

            soup = BeautifulSoup(html, 'xml')
            urls = []

            for item in soup.find_all('item'):
                link = item.find('link')
                if link and link.text:
                    # logNo 추출
                    log_nos = re.findall(r'logNo=(\d+)', link.text)
                    if not log_nos:
                        log_nos = re.findall(rf'/{re.escape(blog_id)}/(\d+)', link.text)

                    if log_nos:
                        urls.append(f"https://blog.naver.com/{blog_id}/{log_nos[0]}")

                if len(urls) >= self.max_posts:
                    break

            return urls
        except Exception as e:
            print(f"❌ RSS 수집 실패: {e}")
            return []

    async def _collect_from_main(self, session: aiohttp.ClientSession, blog_id: str) -> List[str]:
        """PC 메인페이지에서 URL 수집"""
        try:
            main_url = f"https://blog.naver.com/{blog_id}"
            html = await self._fetch(session, main_url)
            if not html:
                return []

            soup = BeautifulSoup(html, 'html.parser')
            iframe = soup.find('iframe', id='mainFrame')

            if iframe and iframe.get('src'):
                inner_url = iframe['src']
                if inner_url.startswith('/'):
                    inner_url = 'https://blog.naver.com' + inner_url

                inner_html = await self._fetch(session, inner_url)
                if inner_html:
                    return self._extract_urls_from_html(inner_html, blog_id)

            return []
        except Exception as e:
            print(f"❌ 메인페이지 수집 실패: {e}")
            return []

    async def _collect_from_postlist(self, session: aiohttp.ClientSession, blog_id: str) -> List[str]:
        """PostList API에서 URL 수집"""
        try:
            url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}&widgetTypeCall=true&directAccess=true"
            html = await self._fetch(session, url)
            if html:
                return self._extract_urls_from_html(html, blog_id)
            return []
        except Exception as e:
            print(f"❌ PostList 수집 실패: {e}")
            return []

    async def _collect_from_mobile(self, session: aiohttp.ClientSession, blog_id: str) -> List[str]:
        """모바일 페이지에서 URL 수집"""
        try:
            url = f"https://m.blog.naver.com/{blog_id}"
            html = await self._fetch(session, url)
            if html:
                return self._extract_urls_from_html(html, blog_id)
            return []
        except Exception as e:
            print(f"❌ 모바일 수집 실패: {e}")
            return []

    def _extract_urls_from_html(self, html: str, blog_id: str) -> List[str]:
        """HTML에서 게시글 URL 추출"""
        urls = []
        patterns = [
            rf'/{re.escape(blog_id)}/(\d+)',
            r'logNo=(\d+)',
            r'data-log-no=["\'](\d+)["\']'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                url = f"https://blog.naver.com/{blog_id}/{match}"
                if url not in urls:
                    urls.append(url)
                if len(urls) >= self.max_posts:
                    break

        return list(dict.fromkeys(urls))[:self.max_posts]

    async def _crawl_single_post(
        self,
        session: aiohttp.ClientSession,
        url: str,
        blog_id: str
    ) -> Optional[Dict]:
        """단일 게시글 크롤링"""
        # PC URL → 모바일 PostView URL 변환
        match = re.search(rf'/{re.escape(blog_id)}/(\d+)', url)
        if not match:
            return None

        log_no = match.group(1)
        mobile_url = f"https://m.blog.naver.com/PostView.naver?blogId={blog_id}&logNo={log_no}"

        html = await self._fetch(session, mobile_url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        # 데이터 추출
        data = {
            'url': url,
            'log_no': log_no,
            'title': self._extract_title(soup),
            'content': self._extract_content(soup),
            'images': self._extract_images(soup),
            'videos': self._extract_videos(soup),
            'hashtags': self._extract_hashtags(soup),
            'post_date': self._extract_date(soup),
            'view_count': self._extract_view_count(soup),
            'comment_count': self._extract_comment_count(soup),
            'sympathy_count': self._extract_sympathy_count(soup),
            'links': self._extract_links(soup),
            'category': self._extract_category(soup)
        }

        return data

    async def _get_blog_info(self, blog_id: str) -> Dict:
        """블로그 정보 수집"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            url = f"https://blog.naver.com/{blog_id}"
            html = await self._fetch(session, url)

            if not html:
                return {"blog_id": blog_id}

            soup = BeautifulSoup(html, 'html.parser')

            # 블로그 제목
            blog_title = "알 수 없음"
            title_tag = soup.find('title')
            if title_tag:
                blog_title = title_tag.text.strip().split(':')[0].strip()

            return {
                "blog_id": blog_id,
                "blog_title": blog_title,
                "blog_url": url
            }

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """제목 추출"""
        # 1. title 태그
        title_tag = soup.find('title')
        if title_tag and title_tag.text:
            return title_tag.text.strip()

        # 2. og:title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()

        return "제목 없음"

    def _extract_content(self, soup: BeautifulSoup) -> Dict:
        """본문 내용 추출"""
        # 전체 텍스트
        text = soup.get_text(separator='\n', strip=True)

        # 문단별 추출
        paragraphs = []
        for tag in soup.find_all(['p', 'div']):
            para_text = tag.get_text(strip=True)
            if para_text and len(para_text) > 10:
                paragraphs.append(para_text)

        return {
            "full_text": text,
            "length": len(text),
            "paragraphs": paragraphs,
            "paragraph_count": len(paragraphs)
        }

    def _extract_images(self, soup: BeautifulSoup) -> List[Dict]:
        """이미지 추출"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                images.append({
                    "url": src,
                    "alt": img.get('alt', ''),
                    "width": img.get('width'),
                    "height": img.get('height')
                })
        return images

    def _extract_videos(self, soup: BeautifulSoup) -> List[Dict]:
        """동영상 추출"""
        videos = []

        # video 태그
        for video in soup.find_all('video'):
            src = video.get('src')
            if src:
                videos.append({"type": "video", "url": src})

        # iframe (유튜브 등)
        for iframe in soup.find_all('iframe'):
            src = iframe.get('src')
            if src:
                videos.append({"type": "iframe", "url": src})

        return videos

    def _extract_hashtags(self, soup: BeautifulSoup) -> List[str]:
        """해시태그 추출"""
        hashtags = []

        # 1. __se-hash-tag
        for tag in soup.find_all('span', class_='__se-hash-tag'):
            text = tag.get_text(strip=True)
            if text:
                hashtags.append(text.replace('#', ''))

        # 2. 하단 태그
        for tag in soup.select('div.wrap_tag a, a.link_tag'):
            text = tag.get_text(strip=True)
            if text:
                hashtags.append(text.replace('#', ''))

        # 3. 메타 태그
        for meta in soup.find_all('meta', attrs={'property': 'og:article:tag'}):
            content = meta.get('content')
            if content:
                hashtags.append(content.strip().replace('#', ''))

        # 중복 제거
        return list(dict.fromkeys(hashtags))

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """포스팅 날짜 추출"""
        # 1. 메타 태그
        date_meta = soup.find('meta', property='article:published_time')
        if date_meta and date_meta.get('content'):
            return date_meta['content'][:10]

        # 2. span.se_publishDate
        date_span = soup.find('span', class_='se_publishDate')
        if date_span:
            date_text = date_span.get_text(strip=True)
            match = re.search(r'(\d{4})[\.\-/](\d{1,2})[\.\-/](\d{1,2})', date_text)
            if match:
                year, month, day = match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # 3. time 태그
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            return time_tag['datetime'][:10]

        return None

    def _extract_view_count(self, soup: BeautifulSoup) -> Optional[int]:
        """조회수 추출"""
        # 1. span.count
        count_span = soup.find('span', class_='count')
        if count_span:
            text = count_span.get_text(strip=True)
            match = re.search(r'[\d,]+', text)
            if match:
                return int(match.group().replace(',', ''))

        # 2. em.cnt
        cnt_em = soup.find('em', class_='cnt')
        if cnt_em:
            text = cnt_em.get_text(strip=True)
            match = re.search(r'[\d,]+', text)
            if match:
                return int(match.group().replace(',', ''))

        return None

    def _extract_comment_count(self, soup: BeautifulSoup) -> Optional[int]:
        """댓글 수 추출"""
        # 1. span.u_cbox_count
        comment_span = soup.find('span', class_='u_cbox_count')
        if comment_span:
            text = comment_span.get_text(strip=True)
            match = re.search(r'\d+', text)
            if match:
                return int(match.group())

        # 2. 댓글 관련 다른 셀렉터
        for selector in ['.comment_count', '.cbox_count']:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                match = re.search(r'\d+', text)
                if match:
                    return int(match.group())

        return None

    def _extract_sympathy_count(self, soup: BeautifulSoup) -> Optional[int]:
        """공감 수 추출"""
        # 1. em.u_cnt
        sympathy_em = soup.find('em', class_='u_cnt')
        if sympathy_em:
            text = sympathy_em.get_text(strip=True)
            match = re.search(r'\d+', text)
            if match:
                return int(match.group())

        # 2. 공감 관련 다른 셀렉터
        for selector in ['.sympathy_count', '.cnt_sympathy']:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                match = re.search(r'\d+', text)
                if match:
                    return int(match.group())

        return None

    def _extract_links(self, soup: BeautifulSoup) -> Dict:
        """링크 추출"""
        internal_links = []
        external_links = []

        for link in soup.find_all('a', href=True):
            href = link['href']

            # 내부 링크 (네이버 블로그)
            if 'blog.naver.com' in href or href.startswith('/'):
                internal_links.append(href)
            else:
                external_links.append(href)

        return {
            "internal": internal_links,
            "external": external_links,
            "total_count": len(internal_links) + len(external_links)
        }

    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """카테고리 추출"""
        # 1. span.category
        category_span = soup.find('span', class_='category')
        if category_span:
            return category_span.get_text(strip=True)

        # 2. meta 태그
        category_meta = soup.find('meta', property='article:section')
        if category_meta and category_meta.get('content'):
            return category_meta['content']

        return None


# 사용 예시
async def main():
    """메인 함수 - 사용 예시"""
    crawler = NaverBlogCrawler(max_posts=30)

    # 블로그 크롤링 (예: coco_hodu_)
    blog_id = "coco_hodu_"
    result = await crawler.crawl_blog(blog_id, save_to_file=True)

    if result:
        print(f"\n📊 크롤링 결과:")
        print(f"   - 블로그: {result['blog_info']['blog_title']}")
        print(f"   - 수집 게시글: {result['total_posts']}개")
        print(f"   - 크롤링 시간: {result['crawled_at']}")


if __name__ == "__main__":
    # 실행
    asyncio.run(main())
