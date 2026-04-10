#!/usr/bin/env python3
"""
출처 추적성 검증 (Source Traceability Checker)
보고서(report-docs.md)의 [S##] 태그가 실제 source_index에 존재하는지 검증한다.
QA Phase 5 Step 2 자동화.

사용법:
  python3 scripts/verify-source-traceability.py <project-directory>
"""

import argparse
import glob
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Set, Tuple

try:
    import yaml
except ImportError:
    print("오류: pyyaml이 설치되지 않았습니다. pip install pyyaml 실행 후 재시도하세요.")
    sys.exit(1)


# ============================================================
# 상수
# ============================================================

# 보고서에서 [S##] 또는 [S###] 태그를 추출하는 정규표현식
TAG_PATTERN = re.compile(r"\[S(\d{1,3})\]")

# 주변 컨텍스트 추출 길이 (앞뒤 각 40자)
CONTEXT_CHARS = 40


# ============================================================
# 헬퍼 함수
# ============================================================

def normalizeSourceId(rawId: str) -> int:
    """
    소스 ID 문자열에서 숫자를 추출하여 정수로 정규화.
    'S01', 'S1', 'S001' → 모두 1로 통일.
    """
    match = re.search(r"(\d+)", str(rawId))
    if match:
        return int(match.group(1))
    return -1


def formatSourceTag(numericId: int) -> str:
    """정수 ID를 표준 태그 형식으로 변환 (S01, S99, S100)."""
    if numericId < 100:
        return f"S{numericId:02d}"
    return f"S{numericId}"


def extractReportTags(reportPath: str) -> List[dict]:
    """
    보고서 파일에서 모든 [S##] 태그를 추출.
    반환: [{ 'numericId': int, 'tag': str, 'location': str, 'context': str }]
    """
    results = []
    if not os.path.isfile(reportPath):
        return results

    with open(reportPath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    filename = os.path.basename(reportPath)

    for lineNum, line in enumerate(lines, start=1):
        for match in TAG_PATTERN.finditer(line):
            numericId = int(match.group(1))
            # 주변 컨텍스트 추출
            start = max(0, match.start() - CONTEXT_CHARS)
            end = min(len(line), match.end() + CONTEXT_CHARS)
            context = line[start:end].strip()

            results.append({
                "numericId": numericId,
                "tag": formatSourceTag(numericId),
                "location": f"{filename}:{lineNum}",
                "context": context,
            })

    return results


def collectSourceIndex(findingsDir: str) -> Dict[int, dict]:
    """
    findings/ 하위 모든 YAML에서 source_index를 수집.
    반환: { numericId: { 'id': str, 'name': str, 'division': str, ... } }
    """
    sources: Dict[int, dict] = {}

    if not os.path.isdir(findingsDir):
        return sources

    yamlFiles = glob.glob(os.path.join(findingsDir, "**/*.yaml"), recursive=True)

    for yamlPath in yamlFiles:
        try:
            with open(yamlPath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data or not isinstance(data, dict):
                continue

            sourceList = data.get("source_index", [])
            if not sourceList or not isinstance(sourceList, list):
                continue

            # Division 추출 (findings/{division}/... 경로에서)
            relPath = os.path.relpath(yamlPath, findingsDir)
            parts = relPath.split(os.sep)
            division = parts[0] if len(parts) > 1 else "unknown"

            for src in sourceList:
                if not isinstance(src, dict):
                    continue
                rawId = src.get("id", "")
                numericId = normalizeSourceId(rawId)
                if numericId < 0:
                    continue

                # 첫 등장만 저장 (중복 시 기존 유지)
                if numericId not in sources:
                    sources[numericId] = {
                        "id": formatSourceTag(numericId),
                        "name": src.get("name", src.get("title", "")),
                        "division": division,
                        "type": src.get("type", ""),
                        "url": src.get("url", ""),
                    }
        except Exception:
            continue

    return sources


def runVerification(projectDir: str) -> dict:
    """
    메인 검증 로직 실행.
    반환: 검증 결과 딕셔너리 (YAML 출력용).
    """
    projectName = os.path.basename(os.path.abspath(projectDir))
    reportPath = os.path.join(projectDir, "reports", "report-docs.md")
    findingsDir = os.path.join(projectDir, "findings")

    # 1. 보고서에서 태그 추출
    reportTags = extractReportTags(reportPath)

    # 보고서 파일 존재 여부 확인
    if not os.path.isfile(reportPath):
        print(f"경고: 보고서 파일을 찾을 수 없습니다: {reportPath}")

    # 2. source_index 수집
    sourceIndex = collectSourceIndex(findingsDir)

    # 3. 고유 태그 ID 집합
    reportTagIds: Set[int] = set()
    for tag in reportTags:
        reportTagIds.add(tag["numericId"])

    sourceIds: Set[int] = set(sourceIndex.keys())

    # 4. 매칭 판정
    matchedIds = reportTagIds & sourceIds
    unmatchedIds = reportTagIds - sourceIds  # 보고서에 있으나 source_index에 없음
    unusedIds = sourceIds - reportTagIds     # source_index에 있으나 보고서 미참조

    # 5. unmatched 상세 정보 (보고서 태그 기준, 첫 등장만)
    unmatchedDetails = []
    seenUnmatched: Set[int] = set()
    for tag in reportTags:
        nid = tag["numericId"]
        if nid in unmatchedIds and nid not in seenUnmatched:
            seenUnmatched.add(nid)
            unmatchedDetails.append({
                "tag": tag["tag"],
                "location": tag["location"],
                "context": tag["context"],
            })
    # 태그 순으로 정렬
    unmatchedDetails.sort(key=lambda x: x["tag"])

    # 6. unused 상세 정보
    unusedDetails = []
    for nid in sorted(unusedIds):
        src = sourceIndex[nid]
        unusedDetails.append({
            "id": src["id"],
            "name": src.get("name", ""),
            "division": src.get("division", ""),
        })

    # 7. 판정
    verdict = "FAIL" if len(unmatchedIds) > 0 else "PASS"

    result = {
        "project": projectName,
        "verified_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "report_file": "reports/report-docs.md",
        "total_tags_in_report": len(reportTagIds),
        "total_sources_in_index": len(sourceIds),
        "matched": len(matchedIds),
        "unmatched": unmatchedDetails if unmatchedDetails else [],
        "unused": unusedDetails if unusedDetails else [],
        "verdict": verdict,
    }

    return result


def writeResultYaml(result: dict, outputPath: str):
    """검증 결과를 YAML 파일로 저장."""
    outputDir = os.path.dirname(outputPath)
    if outputDir and not os.path.isdir(outputDir):
        os.makedirs(outputDir, exist_ok=True)

    # YAML 출력 시 한국어 깨짐 방지
    with open(outputPath, "w", encoding="utf-8") as f:
        yaml.dump(
            result,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


def printConsoleSummary(result: dict):
    """콘솔에 요약 결과를 출력."""
    verdict = result["verdict"]
    marker = "✓ PASS" if verdict == "PASS" else "✗ FAIL"

    print()
    print("=" * 60)
    print(f"  Source Traceability Check: {marker}")
    print("=" * 60)
    print(f"  프로젝트       : {result['project']}")
    print(f"  보고서 파일    : {result['report_file']}")
    print(f"  검증 시각      : {result['verified_at']}")
    print("-" * 60)
    print(f"  보고서 태그 수 : {result['total_tags_in_report']}")
    print(f"  소스 인덱스 수 : {result['total_sources_in_index']}")
    print(f"  매칭           : {result['matched']}")
    print(f"  미매칭 (ERROR) : {len(result['unmatched'])}")
    print(f"  미참조 (WARN)  : {len(result['unused'])}")
    print("-" * 60)

    if result["unmatched"]:
        print()
        print("  [ERROR] 보고서에 있으나 source_index에 없는 태그:")
        for item in result["unmatched"]:
            print(f"    - {item['tag']}  @ {item['location']}")
            print(f"      \"{item['context']}\"")

    if result["unused"]:
        print()
        print("  [WARNING] source_index에 있으나 보고서에서 미참조:")
        for item in result["unused"]:
            print(f"    - {item['id']}  ({item['name']})  [{item['division']}]")

    print()
    print(f"  최종 판정: {marker}")
    print("=" * 60)
    print()


# ============================================================
# 메인 엔트리포인트
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="보고서 [S##] 태그 ↔ source_index 추적성 검증 (QA Phase 5 Step 2)"
    )
    parser.add_argument(
        "project",
        help="프로젝트 디렉토리 경로 (예: my-research-project)"
    )
    args = parser.parse_args()

    # 프로젝트 디렉토리 탐색
    projectDir = os.path.abspath(args.project)
    if not os.path.isdir(projectDir):
        print(f"오류: 프로젝트 디렉토리를 찾을 수 없습니다: {projectDir}")
        sys.exit(1)

    # 검증 실행
    result = runVerification(projectDir)

    # YAML 결과 파일 저장
    outputPath = os.path.join(projectDir, "qa", "source-traceability.yaml")
    writeResultYaml(result, outputPath)

    # 콘솔 요약 출력
    printConsoleSummary(result)

    print(f"  결과 저장: {outputPath}")
    print()

    # 종료 코드: FAIL이면 1
    if result["verdict"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
