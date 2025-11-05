"""
네이버 블로그 분석기 - 웹 버전
2025 네이버 C-Rank 기준
- 다중 폴백 URL 수집 (PC → iframe → 모바일 → RSS)
- 모바일 PostView로 안정적 파싱
- 세분화된 점수 체계 (SEO + 콘텐츠)
- 등급제 (S~F)
- 비동기 HTTP 요청으로 빠른 크롤링
- 포스팅 날짜, 조회수 추출
"""
import re
import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime

class BlogAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36',
            'Referer': 'https://blog.naver.com/',
            'Accept-Language': 'ko-KR,ko;q=0.9'
        }
        self.timeout = 12
        self.max_posts = 30  # 최대 게시글 수 증가
    
    def analyze(self, blog_id):
        """블로그 전체 분석 (동기 래퍼)"""
        try:
            # 비동기 함수를 동기적으로 실행
            return asyncio.run(self._analyze_async(blog_id))
        except Exception as e:
            print(f"분석 오류: {e}")
            return None

    async def _analyze_async(self, blog_id):
        """블로그 전체 분석 (비동기)"""
        try:
            # 1. 게시글 URL 수집 (다중 폴백)
            post_urls = await self._get_recent_post_urls_async(blog_id)
            if not post_urls:
                return None

            # 2. 각 게시글 병렬 분석 (최대 30개)
            post_results = []
            async with aiohttp.ClientSession(headers=self.headers) as session:
                tasks = [
                    self._analyze_single_post_async(session, url, blog_id)
                    for url in post_urls[:self.max_posts]
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # 성공한 결과만 추가
                for result in results:
                    if result and not isinstance(result, Exception):
                        post_results.append(result)

            if not post_results:
                return None

            # 3. 블로그 전체 랭크 계산
            blog_rank, traffic_rank = self._calculate_blog_rank(post_results)

            return {
                "blog_id": blog_id,
                "total_posts": len(post_results),
                "posts": post_results,
                "blog_rank": blog_rank,
                "traffic_rank": traffic_rank,
                "analyzed_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"분석 오류: {e}")
            return None
    
    def _fetch(self, url, timeout=None):
        """HTTP 요청 (동기)"""
        res = requests.get(url, headers=self.headers, timeout=timeout or self.timeout)
        if not res.encoding or res.encoding.lower() in ("iso-8859-1", "ansi"):
            res.encoding = res.apparent_encoding
        res.raise_for_status()
        return res

    async def _fetch_async(self, session, url, timeout=None):
        """HTTP 요청 (비동기)"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout or self.timeout)) as response:
                response.raise_for_status()
                text = await response.text()
                return text
        except Exception as e:
            print(f"HTTP 요청 실패 ({url}): {e}")
            return None
    
    def _get_recent_post_urls(self, blog_id):
        """게시글 URL 수집 (다중 폴백)"""
        urls = []
        
        # 방법 1: PC 메인 → iframe
        try:
            main_url = f"https://blog.naver.com/{blog_id}"
            res = self._fetch(main_url)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # iframe 찾기
            iframe = soup.find('iframe', id='mainFrame')
            if iframe and iframe.get('src'):
                inner_url = iframe['src']
                if inner_url.startswith('/'):
                    inner_url = 'https://blog.naver.com' + inner_url
                
                res2 = self._fetch(inner_url)
                urls = self._extract_urls_from_html(res2.text, blog_id)
                
                if urls:
                    return urls[:10]
        except:
            pass
        
        # 방법 2: PostList (구형)
        try:
            list_url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}&widgetTypeCall=true&directAccess=true"
            res = self._fetch(list_url)
            urls = self._extract_urls_from_html(res.text, blog_id)
            
            if urls:
                return urls[:10]
        except:
            pass
        
        # 방법 3: 모바일 홈
        try:
            mobile_url = f"https://m.blog.naver.com/{blog_id}"
            res = self._fetch(mobile_url)
            urls = self._extract_urls_from_html(res.text, blog_id)
            
            if urls:
                return urls[:10]
        except:
            pass
        
        # 방법 4: RSS
        try:
            rss_url = f"https://rss.blog.naver.com/{blog_id}.xml"
            res = self._fetch(rss_url)
            soup = BeautifulSoup(res.text, 'xml')
            
            urls = []
            for item in soup.find_all('item'):
                link = item.find('link')
                if link and link.text:
                    log_nos = re.findall(r'logNo=(\d+)', link.text)
                    if not log_nos:
                        log_nos = re.findall(rf'/{re.escape(blog_id)}/(\d+)', link.text)
                    if log_nos:
                        urls.append(f"https://blog.naver.com/{blog_id}/{log_nos[0]}")
                if len(urls) >= 10:
                    break
            
            if urls:
                return urls[:10]
        except:
            pass
        
        return []

    async def _get_recent_post_urls_async(self, blog_id):
        """게시글 URL 수집 (비동기, 다중 폴백)"""
        async with aiohttp.ClientSession(headers=self.headers) as session:
            urls = []

            # 방법 1: PC 메인 → iframe
            try:
                main_url = f"https://blog.naver.com/{blog_id}"
                html = await self._fetch_async(session, main_url)
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    iframe = soup.find('iframe', id='mainFrame')
                    if iframe and iframe.get('src'):
                        inner_url = iframe['src']
                        if inner_url.startswith('/'):
                            inner_url = 'https://blog.naver.com' + inner_url

                        inner_html = await self._fetch_async(session, inner_url)
                        if inner_html:
                            urls = self._extract_urls_from_html(inner_html, blog_id)
                            if urls:
                                return urls[:self.max_posts]
            except Exception as e:
                print(f"방법 1 실패: {e}")

            # 방법 2: PostList (구형)
            try:
                list_url = f"https://blog.naver.com/PostList.naver?blogId={blog_id}&widgetTypeCall=true&directAccess=true"
                html = await self._fetch_async(session, list_url)
                if html:
                    urls = self._extract_urls_from_html(html, blog_id)
                    if urls:
                        return urls[:self.max_posts]
            except Exception as e:
                print(f"방법 2 실패: {e}")

            # 방법 3: 모바일 홈
            try:
                mobile_url = f"https://m.blog.naver.com/{blog_id}"
                html = await self._fetch_async(session, mobile_url)
                if html:
                    urls = self._extract_urls_from_html(html, blog_id)
                    if urls:
                        return urls[:self.max_posts]
            except Exception as e:
                print(f"방법 3 실패: {e}")

            # 방법 4: RSS
            try:
                rss_url = f"https://rss.blog.naver.com/{blog_id}.xml"
                html = await self._fetch_async(session, rss_url)
                if html:
                    soup = BeautifulSoup(html, 'xml')
                    urls = []
                    for item in soup.find_all('item'):
                        link = item.find('link')
                        if link and link.text:
                            log_nos = re.findall(r'logNo=(\d+)', link.text)
                            if not log_nos:
                                log_nos = re.findall(rf'/{re.escape(blog_id)}/(\d+)', link.text)
                            if log_nos:
                                urls.append(f"https://blog.naver.com/{blog_id}/{log_nos[0]}")
                        if len(urls) >= self.max_posts:
                            break

                    if urls:
                        return urls[:self.max_posts]
            except Exception as e:
                print(f"방법 4 실패: {e}")

            return []

    def _extract_urls_from_html(self, html, blog_id):
        """HTML에서 게시글 URL 추출"""
        urls = []
        
        # 정규표현식으로 추출
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
                if len(urls) >= 10:
                    break
        
        return list(dict.fromkeys(urls))[:10]  # 중복 제거
    
    def _to_mobile_postview(self, url, blog_id):
        """PC URL → 모바일 PostView URL 변환"""
        match = re.search(rf'https?://blog\.naver\.com/{re.escape(blog_id)}/(\d+)', url)
        if match:
            return f"https://m.blog.naver.com/PostView.naver?blogId={blog_id}&logNo={match.group(1)}"
        
        match = re.search(r'logNo=(\d+)', url)
        if match:
            return f"https://m.blog.naver.com/PostView.naver?blogId={blog_id}&logNo={match.group(1)}"
        
        return None
    
    def _analyze_single_post(self, url, blog_id):
        """개별 게시글 분석"""
        # 모바일 PostView로 변환
        mobile_url = self._to_mobile_postview(url, blog_id)
        if not mobile_url:
            return None
        
        try:
            res = self._fetch(mobile_url)
            soup = BeautifulSoup(res.text, 'html.parser')
        except:
            return None
        
        # 데이터 추출
        post_data = self._extract_post_data(soup, url)
        
        # 점수 계산
        seo_score, seo_issues = self._calculate_seo_score(post_data)
        content_score, content_issues = self._calculate_content_score(post_data)
        
        total_score = int(seo_score * 0.4 + content_score * 0.6)
        
        return {
            'title': post_data['title'][:50] + '...' if len(post_data['title']) > 50 else post_data['title'],
            'url': url,
            'total_score': total_score,
            'seo_score': seo_score,
            'content_score': content_score,
            'text_length': post_data['text_length'],
            'image_count': post_data['image_count'],
            'video_count': post_data['video_count'],
            'hashtag_count': len(post_data['hashtags']),
            'link_count': post_data['link_count'],
            'issues': seo_issues + content_issues
        }

    async def _analyze_single_post_async(self, session, url, blog_id):
        """개별 게시글 분석 (비동기)"""
        # 모바일 PostView로 변환
        mobile_url = self._to_mobile_postview(url, blog_id)
        if not mobile_url:
            return None

        try:
            html = await self._fetch_async(session, mobile_url)
            if not html:
                return None

            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"게시글 파싱 실패 ({url}): {e}")
            return None

        # 데이터 추출
        post_data = self._extract_post_data(soup, url)

        # 점수 계산
        seo_score, seo_issues = self._calculate_seo_score(post_data)
        content_score, content_issues = self._calculate_content_score(post_data)

        total_score = int(seo_score * 0.4 + content_score * 0.6)

        result = {
            'title': post_data['title'][:50] + '...' if len(post_data['title']) > 50 else post_data['title'],
            'url': url,
            'total_score': total_score,
            'seo_score': seo_score,
            'content_score': content_score,
            'text_length': post_data['text_length'],
            'image_count': post_data['image_count'],
            'video_count': post_data['video_count'],
            'hashtag_count': len(post_data['hashtags']),
            'link_count': post_data['link_count'],
            'issues': seo_issues + content_issues
        }

        # 포스팅 날짜 추가
        if post_data.get('post_date'):
            result['post_date'] = post_data['post_date']

        # 조회수 추가
        if post_data.get('view_count'):
            result['view_count'] = post_data['view_count']

        return result

    def _extract_post_data(self, soup, url):
        """게시글 데이터 추출"""
        # 제목
        title = '제목 없음'
        title_tag = soup.find('title')
        if title_tag and title_tag.text:
            title = title_tag.text.strip()
        else:
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title = og_title['content'].strip()
        
        # 해시태그 (다중 소스)
        hashtags = []
        # 1) 본문 __se-hash-tag
        hashtags.extend(t.get_text(strip=True) for t in soup.find_all('span', class_='__se-hash-tag'))
        # 2) 하단 태그
        hashtags.extend(a.get_text(strip=True) for a in soup.select('div.wrap_tag a'))
        hashtags.extend(a.get_text(strip=True) for a in soup.select('a.link_tag'))
        # 3) 메타 태그
        for meta in soup.find_all('meta', attrs={'property': 'og:article:tag'}):
            if meta.get('content'):
                hashtags.append(meta['content'].strip())
        
        # 해시태그 정규화
        normalized_tags = []
        seen = set()
        for tag in hashtags:
            if not tag:
                continue
            tag = tag if tag.startswith('#') else ('#' + tag)
            if tag not in seen:
                normalized_tags.append(tag[1:])  # # 제거
                seen.add(tag)
        
        # 본문 텍스트
        content_text = soup.get_text(separator=' ', strip=True)
        
        # 문단 추출
        paragraphs = []
        for p_tag in soup.find_all(['p', 'div']):
            text = p_tag.get_text(strip=True)
            if text and len(text) > 10:
                paragraphs.append(text)
        
        # 이미지
        images = soup.find_all('img')
        
        # 동영상
        videos = soup.find_all(['video', 'iframe'])
        
        # 링크
        links = soup.find_all('a', href=True)

        # 포스팅 날짜 추출 (다중 소스)
        post_date = None
        try:
            # 1. 메타 태그
            date_meta = soup.find('meta', property='article:published_time')
            if date_meta and date_meta.get('content'):
                post_date = date_meta['content'][:10]  # YYYY-MM-DD 형식

            # 2. span.se_publishDate
            if not post_date:
                date_span = soup.find('span', class_='se_publishDate')
                if date_span:
                    date_text = date_span.get_text(strip=True)
                    # 날짜 파싱 (예: "2025.01.15." → "2025-01-15")
                    date_match = re.search(r'(\d{4})[\.\-/](\d{1,2})[\.\-/](\d{1,2})', date_text)
                    if date_match:
                        year, month, day = date_match.groups()
                        post_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # 3. time 태그
            if not post_date:
                time_tag = soup.find('time')
                if time_tag and time_tag.get('datetime'):
                    post_date = time_tag['datetime'][:10]
        except Exception as e:
            print(f"날짜 추출 실패: {e}")

        # 조회수 추출
        view_count = None
        try:
            # 1. span.count
            count_span = soup.find('span', class_='count')
            if count_span:
                view_text = count_span.get_text(strip=True)
                # "조회 1,234" → 1234
                view_match = re.search(r'[\d,]+', view_text)
                if view_match:
                    view_count = int(view_match.group().replace(',', ''))

            # 2. em.cnt
            if view_count is None:
                cnt_em = soup.find('em', class_='cnt')
                if cnt_em:
                    view_text = cnt_em.get_text(strip=True)
                    view_match = re.search(r'[\d,]+', view_text)
                    if view_match:
                        view_count = int(view_match.group().replace(',', ''))
        except Exception as e:
            print(f"조회수 추출 실패: {e}")

        result = {
            'title': title,
            'url': url,
            'text': content_text,
            'text_length': len(content_text),
            'paragraphs': paragraphs,
            'paragraph_count': len(paragraphs),
            'first_paragraph': paragraphs[0] if paragraphs else '',
            'hashtags': normalized_tags,
            'image_count': len(images),
            'video_count': len(videos),
            'link_count': len(links)
        }

        # 선택적 필드 추가
        if post_date:
            result['post_date'] = post_date
        if view_count is not None:
            result['view_count'] = view_count

        return result
    
    def _extract_keywords(self, title, top_n=3):
        """제목에서 핵심 키워드 추출"""
        title = re.sub(r'[^\w\s]', ' ', title)
        words = [w for w in title.split() if len(w) >= 2]
        
        stopwords = ['이번', '오늘', '어제', '그리고', '하지만', '그래서', '그런데',
                     '있는', '없는', '되는', '하는', '이렇게', '저렇게', '정말', '진짜',
                     '너무', '아주', '매우', '완전', '후기', '리뷰', '추천']
        words = [w for w in words if w not in stopwords]
        
        if not words:
            return []
        
        word_freq = Counter(words)
        return [word for word, count in word_freq.most_common(top_n)]
    
    def _calculate_seo_score(self, post_data):
        """SEO 점수 계산 (100점 만점, 감점식)"""
        score = 100
        issues = []
        
        title = post_data['title']
        hashtags = post_data['hashtags']
        text = post_data['text']
        first_paragraph = post_data['first_paragraph']
        link_count = post_data['link_count']
        
        # 1. 제목 길이 (15~40자 권장)
        title_len = len(title)
        if title_len < 15:
            score -= 10
            issues.append(f"제목이 짧음 ({title_len}자)")
        elif title_len > 40:
            score -= 5
            issues.append(f"제목이 김 ({title_len}자)")
        
        # 2. 해시태그 (8~10개 최적)
        tag_count = len(hashtags)
        if 8 <= tag_count <= 10:
            pass
        elif 5 <= tag_count < 8:
            score -= 5
            issues.append(f"해시태그 부족 ({tag_count}개)")
        elif 3 <= tag_count < 5:
            score -= 10
            issues.append(f"해시태그 많이 부족 ({tag_count}개)")
        elif tag_count == 0:
            score -= 20
            issues.append("해시태그 없음")
        elif tag_count < 3:
            score -= 15
            issues.append(f"해시태그 매우 부족 ({tag_count}개)")
        elif tag_count > 15:
            score -= 8
            issues.append(f"해시태그 과다 ({tag_count}개)")
        
        # 3. 키워드 분석
        keywords = self._extract_keywords(title)
        if keywords:
            # 키워드-해시태그 일치
            keyword_in_hashtag = sum(1 for kw in keywords if kw in hashtags)
            if keyword_in_hashtag == 0:
                score -= 10
                issues.append("키워드와 해시태그 불일치")
            
            # 도입부에 키워드
            first_200 = first_paragraph[:200] if len(first_paragraph) > 200 else first_paragraph
            keyword_in_first = sum(1 for kw in keywords if kw in first_200)
            if keyword_in_first == 0 and len(first_paragraph) > 0:
                score -= 8
                issues.append("도입부에 키워드 없음")
            
            # 키워드 밀도
            if len(text) > 0:
                keyword_count = sum(text.count(kw) for kw in keywords)
                if keyword_count < 3:
                    score -= 7
                    issues.append(f"키워드 반복 부족 ({keyword_count}회)")
                elif keyword_count > 10:
                    score -= 5
                    issues.append(f"키워드 과다 ({keyword_count}회)")
        
        # 4. 링크
        if link_count == 0:
            score -= 5
            issues.append("링크 없음")
        elif link_count > 10:
            score -= 3
            issues.append(f"링크 과다 ({link_count}개)")
        
        return max(0, score), issues
    
    def _calculate_content_score(self, post_data):
        """콘텐츠 품질 점수 (100점 만점)"""
        score = 0
        issues = []
        
        text_length = post_data['text_length']
        image_count = post_data['image_count']
        video_count = post_data['video_count']
        paragraph_count = post_data['paragraph_count']
        paragraphs = post_data['paragraphs']
        
        # 1. 글자수 (45점)
        if text_length >= 3000:
            score += 45
        elif text_length >= 2500:
            score += 40
        elif text_length >= 2000:
            score += 35
        elif text_length >= 1500:
            score += 25
            issues.append(f"글자수 부족 ({text_length}자)")
        elif text_length >= 1000:
            score += 15
            issues.append(f"글자수 많이 부족 ({text_length}자)")
        elif text_length >= 500:
            score += 5
            issues.append(f"글자수 매우 부족 ({text_length}자)")
        else:
            issues.append(f"글자수 심각하게 부족 ({text_length}자)")
        
        # 2. 이미지 (35점)
        if image_count >= 10:
            score += 35
        elif image_count >= 7:
            score += 30
        elif image_count >= 5:
            score += 25
            issues.append(f"이미지 부족 ({image_count}장)")
        elif image_count >= 3:
            score += 15
            issues.append(f"이미지 많이 부족 ({image_count}장)")
        elif image_count >= 1:
            score += 5
            issues.append(f"이미지 매우 부족 ({image_count}장)")
        else:
            issues.append("이미지 없음")
        
        # 3. 동영상 (10점)
        if video_count >= 1:
            score += 10
        
        # 4. 문단 구조 (10점)
        if paragraph_count >= 8:
            score += 10
        elif paragraph_count >= 5:
            score += 7
        elif paragraph_count >= 3:
            score += 5
            issues.append(f"문단 부족 ({paragraph_count}개)")
        elif paragraph_count >= 1:
            score += 3
            issues.append(f"문단 매우 부족 ({paragraph_count}개)")
        else:
            issues.append("문단 구조 없음")
        
        # 문단 길이 체크
        if paragraphs:
            long_paragraphs = sum(1 for p in paragraphs if len(p) > 300)
            if long_paragraphs > paragraph_count * 0.4:
                score -= 3
                issues.append("일부 문단이 너무 김")
        
        return score, issues
    
    def _calculate_blog_rank(self, post_results):
        """블로그 전체 랭크 계산"""
        if not post_results:
            return "F", "F등급 (분석 불가)"
        
        # 평균 점수
        avg_score = sum(p['total_score'] for p in post_results) / len(post_results)
        
        # 블로그 랭크
        if avg_score >= 90:
            blog_rank = "S"
        elif avg_score >= 80:
            blog_rank = "A"
        elif avg_score >= 70:
            blog_rank = "B"
        elif avg_score >= 60:
            blog_rank = "C"
        elif avg_score >= 50:
            blog_rank = "D"
        else:
            blog_rank = "F"
        
        # 예상 유입 랭크
        if avg_score >= 90:
            traffic_rank = "S등급 (매우 높음)"
        elif avg_score >= 80:
            traffic_rank = "A등급 (높음)"
        elif avg_score >= 70:
            traffic_rank = "B등급 (보통)"
        elif avg_score >= 60:
            traffic_rank = "C등급 (낮음)"
        elif avg_score >= 50:
            traffic_rank = "D등급 (매우 낮음)"
        else:
            traffic_rank = "F등급 (기대 어려움)"
        
        return blog_rank, traffic_rank
