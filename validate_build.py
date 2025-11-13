#!/usr/bin/env python3
"""
빌드 전 검증 스크립트
Build validation script
"""

import os
import sys

def check_file_exists(filepath, description):
    """파일 존재 여부 확인"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} 없음: {filepath}")
        return False

def check_module_import(module_name):
    """모듈 import 가능 여부 확인"""
    try:
        __import__(module_name)
        print(f"✅ 모듈 설치됨: {module_name}")
        return True
    except ImportError:
        print(f"❌ 모듈 없음: {module_name}")
        return False

def main():
    print("=" * 80)
    print("🔍 빌드 전 검증")
    print("=" * 80)
    print()

    all_ok = True

    # 1. 필수 파일 확인
    print("📁 필수 파일 확인...")
    print("-" * 80)
    files = [
        ("blog_optimizer_gui.py", "메인 GUI 프로그램"),
        ("advanced_seo_optimizer.py", "고급 최적화 엔진"),
        ("blog_optimizer.py", "기본 최적화 엔진"),
        ("금칙어 수정사항 모음.txt", "금칙어 데이터"),
        ("blog_optimizer.spec", "PyInstaller 설정"),
        ("requirements.txt", "의존성 목록"),
    ]

    for filepath, desc in files:
        if not check_file_exists(filepath, desc):
            all_ok = False

    print()

    # 2. 필수 Python 모듈 확인
    print("🐍 필수 모듈 확인...")
    print("-" * 80)
    modules = [
        "pandas",
        "openpyxl",
        "anthropic",
        "tkinter",
        "threading",
        "re",
        "random",
    ]

    for module in modules:
        if not check_module_import(module):
            all_ok = False

    print()

    # 3. PyInstaller 확인
    print("🔨 빌드 도구 확인...")
    print("-" * 80)
    if not check_module_import("PyInstaller"):
        all_ok = False
        print("   → pip install pyinstaller")

    print()

    # 4. spec 파일 문법 확인
    print("📝 spec 파일 검증...")
    print("-" * 80)
    try:
        with open("blog_optimizer.spec", "r", encoding="utf-8") as f:
            spec_content = f.read()
            compile(spec_content, "blog_optimizer.spec", "exec")
        print("✅ spec 파일 문법 정상")
    except SyntaxError as e:
        print(f"❌ spec 파일 문법 오류: {e}")
        all_ok = False
    except Exception as e:
        print(f"⚠️ spec 파일 검증 중 오류: {e}")

    print()

    # 5. 금칙어 파일 형식 확인
    print("📋 데이터 파일 검증...")
    print("-" * 80)
    try:
        with open("금칙어 수정사항 모음.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(f"✅ 금칙어 파일: {len(lines)}줄")
    except Exception as e:
        print(f"❌ 금칙어 파일 오류: {e}")
        all_ok = False

    print()

    # 6. GUI 파일 간단 검증
    print("🖥️ GUI 프로그램 검증...")
    print("-" * 80)
    try:
        with open("blog_optimizer_gui.py", "r", encoding="utf-8") as f:
            gui_content = f.read()
            if "class BlogOptimizerGUI" in gui_content:
                print("✅ GUI 클래스 발견")
            else:
                print("⚠️ GUI 클래스를 찾을 수 없음")
                all_ok = False
    except Exception as e:
        print(f"❌ GUI 파일 오류: {e}")
        all_ok = False

    print()
    print("=" * 80)

    if all_ok:
        print("✅ 모든 검증 통과! 빌드를 시작할 수 있습니다.")
        print()
        print("다음 단계:")
        print("  Windows: build.bat")
        print("  Linux/Mac: ./build.sh")
        return 0
    else:
        print("❌ 검증 실패! 위의 오류를 수정한 후 다시 시도하세요.")
        print()
        print("누락된 패키지 설치:")
        print("  pip install -r requirements.txt")
        print("  pip install pyinstaller")
        return 1

if __name__ == "__main__":
    sys.exit(main())
