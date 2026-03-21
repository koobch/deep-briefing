#!/bin/bash
# quickstart.sh — 비인터랙티브 환경 점검 전용
# 사용법: ./scripts/quickstart.sh
#
# 참고: 인터랙티브 설정은 Claude Code에서 /setup 명령을 사용하세요.
# /setup이 환경 점검 → 도메인 생성 → API 설정을 대화형으로 안내합니다.
# 이 스크립트는 CI/CD 또는 스크립트에서 호출하는 비인터랙티브 환경 점검 전용입니다.

set -e

echo "=== Deep-Briefing — 초기 설정 ==="
echo ""

# 1. Python 의존성 확인 + 설치
echo "[1/4] Python 의존성 확인..."
if command -v python3 &>/dev/null; then
    echo "  ✅ Python3 $(python3 --version | awk '{print $2}')"
else
    echo "  ❌ Python3가 필요합니다. https://www.python.org/downloads/"
    exit 1
fi

if command -v pip3 &>/dev/null || command -v pip &>/dev/null; then
    pip install -r requirements.txt -q 2>/dev/null || pip3 install -r requirements.txt -q
    echo "  ✅ 의존성 설치 완료"
else
    echo "  ⚠️  pip를 찾을 수 없습니다. 수동으로 설치해 주세요: pip install -r requirements.txt"
fi

# 2. tmux 확인
echo ""
echo "[2/4] tmux 확인..."
if command -v tmux &>/dev/null; then
    echo "  ✅ tmux $(tmux -V)"
else
    echo "  ⚠️  tmux가 없습니다. Division 병렬 실행에 필요합니다."
    echo "  설치: brew install tmux (macOS) / sudo apt install tmux (Linux)"
fi

# 3. .env 설정
echo ""
echo "[3/4] 환경 변수 설정..."
if [ -f .env ]; then
    echo "  ✅ .env 파일 이미 존재"
else
    cp .env.example .env
    echo "  ✅ .env 파일 생성됨 (.env.example → .env)"
    echo "  💡 API 키를 설정하면 데이터 품질이 향상됩니다 (선택사항)"
    echo "     → .env 파일을 열어 필요한 키를 입력하세요"
    echo "     → 키 없이도 웹 검색으로 리서치 가능합니다"
fi

# 4. Claude Code 확인
echo ""
echo "[4/4] Claude Code 확인..."
if command -v claude &>/dev/null; then
    echo "  ✅ Claude Code 설치됨"
else
    echo "  ❌ Claude Code CLI가 필요합니다."
    echo "  설치: https://docs.anthropic.com/en/docs/claude-code"
    echo ""
    echo "  Claude Code 없이는 리서치를 실행할 수 없습니다."
fi

echo ""
echo "=== 설정 완료 ==="
echo ""
echo "다음 단계:"
echo "  1. 프로젝트 초기화: ./scripts/init-project.sh my-first-research"
echo "  2. Claude Code 실행: claude"
echo "  3. 리서치 시작:     /research interactive my-first-research {주제}"
echo ""
echo "상세 가이드: README.md"
