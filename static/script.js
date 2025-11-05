// 블로그 분석 실행
async function analyzeBlog() {
    const blogId = document.getElementById('blog-id').value.trim();
    
    if (!blogId) {
        alert('블로그 ID를 입력해주세요');
        return;
    }
    
    // UI 상태 변경
    document.getElementById('result').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('analyze-btn').disabled = true;
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ blog_id: blogId })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '분석 중 오류가 발생했습니다');
        }
        
        const data = await response.json();
        displayResult(data);
        
    } catch (error) {
        alert(error.message);
    } finally {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('analyze-btn').disabled = false;
    }
}

// 결과 표시
function displayResult(data) {
    const resultDiv = document.getElementById('result');
    
    const html = `
        <div class="result-header">
            <h2>분석 결과</h2>
            <div class="blog-info">
                블로그 ID: ${data.blog_id} | 분석 게시글: ${data.total_posts}개
            </div>
        </div>
        
        <div class="rank-cards">
            <div class="rank-card">
                <h3>블로그 전체 랭크</h3>
                <div class="rank ${data.blog_rank}">${data.blog_rank}</div>
                <div class="description">${getRankDescription(data.blog_rank)}</div>
            </div>
            
            <div class="rank-card">
                <h3>예상 유입 랭크</h3>
                <div class="rank ${data.traffic_rank.split('등급')[0]}">${data.traffic_rank}</div>
            </div>
        </div>
        
        <div class="posts-section">
            <h3>📝 게시글별 분석 (최근 ${data.posts.length}개)</h3>
            ${data.posts.map((post, index) => createPostCard(post, index + 1)).join('')}
        </div>
    `;
    
    resultDiv.innerHTML = html;
    resultDiv.classList.remove('hidden');
    
    // 결과로 스크롤
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 게시글 카드 생성
function createPostCard(post, index) {
    const stars = getStars(post.total_score);
    
    return `
        <div class="post-item">
            <div class="post-title">${index}. ${post.title}</div>
            
            <div class="post-scores">
                <div class="score-badge">
                    <span class="label">종합 점수</span>
                    <span class="value">${post.total_score}점 ${stars}</span>
                </div>
                <div class="score-badge">
                    <span class="label">SEO</span>
                    <span class="value">${post.seo_score}점</span>
                </div>
                <div class="score-badge">
                    <span class="label">콘텐츠</span>
                    <span class="value">${post.content_score}점</span>
                </div>
            </div>
            
            <div class="post-stats">
                <span>📝 ${post.text_length.toLocaleString()}자</span>
                <span>🖼️ ${post.image_count}장</span>
                <span>🎬 ${post.video_count}개</span>
                <span>#️⃣ ${post.hashtag_count}개</span>
                <span>🔗 ${post.link_count}개</span>
            </div>
            
            ${post.issues.length > 0 ? `
                <div class="post-issues">
                    <div class="label">⚠️ 개선 사항</div>
                    <div class="issue-list">${post.issues.slice(0, 3).join(', ')}</div>
                </div>
            ` : ''}
        </div>
    `;
}

// 별점 생성
function getStars(score) {
    const count = Math.floor(score / 20);
    return '⭐'.repeat(count);
}

// 랭크 설명
function getRankDescription(rank) {
    const descriptions = {
        'S': '최고 수준',
        'A': '우수함',
        'B': '보통',
        'C': '개선 필요',
        'D': '많은 개선 필요',
        'F': '전면 재작성 권장'
    };
    return descriptions[rank] || '';
}

// Enter 키로 분석 실행
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('blog-id').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeBlog();
        }
    });
});
