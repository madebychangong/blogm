"""
네이버 블로그 분석기 - FastAPI 웹 서버
무료 버전: 기본 SEO 및 콘텐츠 품질 분석
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
from analyzer import BlogAnalyzer

app = FastAPI(title="네이버 블로그 분석기", version="1.0.0")

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

# 요청 모델
class AnalyzeRequest(BaseModel):
    blog_id: str

# 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def main_page():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# 블로그 분석 API
@app.post("/api/analyze")
async def analyze_blog(request: AnalyzeRequest):
    """블로그 분석 실행"""
    try:
        blog_id = request.blog_id.strip()
        
        if not blog_id:
            raise HTTPException(status_code=400, detail="블로그 ID를 입력해주세요")
        
        # 분석 실행
        analyzer = BlogAnalyzer()
        result = analyzer.analyze(blog_id)
        
        if result is None:
            raise HTTPException(status_code=404, detail="블로그를 찾을 수 없습니다")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 헬스체크
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
