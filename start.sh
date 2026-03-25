#!/bin/bash
# start.sh — Deep-Briefing 시작 스크립트
# 환경 상태를 먼저 보여주고, Claude를 실행합니다.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║        Deep-Briefing 시작합니다          ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# 환경 상태 점검 (사람이 읽는 버전)
DOMAINS=$(find domains -maxdepth 1 -type d ! -name "domains" ! -name "example" 2>/dev/null)
PROJECTS=$(find . -maxdepth 2 -name "00-client-brief.md" 2>/dev/null | head -5)

if [ -z "$DOMAINS" ] && [ -z "$PROJECTS" ]; then
  echo "  처음 사용하시는군요!"
  echo ""
  echo "  Claude가 실행되면 /setup 을 입력해주세요."
  echo "  환경 설정이 자동으로 진행됩니다. (약 2분)"
  echo ""
elif [ -z "$PROJECTS" ]; then
  echo "  설정이 완료된 상태입니다."
  echo ""
  echo "  Claude가 실행되면 리서치 주제를 말씀해주세요."
  echo "  예: /research interactive my-project 한국 SaaS 시장 진출 전략"
  echo ""
else
  echo "  진행 중인 프로젝트:"
  for p in $PROJECTS; do
    name=$(basename "$(dirname "$p")")
    echo "    - $name"
  done
  echo ""
  echo "  Claude가 실행되면 이어서 진행하거나 새 리서치를 시작하세요."
  echo ""
fi

echo "  ──────────────────────────────────────────"
echo "  Claude를 실행합니다..."
echo ""

claude
