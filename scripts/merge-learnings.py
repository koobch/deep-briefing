#!/usr/bin/env python3
"""
프로젝트 학습 결과를 도메인 지식 베이스에 머지.
Division Lead가 추출한 {project}/learnings/{division}-learnings.yaml을
domains/{domain}/knowledge/*.yaml에 통합한다.

사용법:
  python scripts/merge-learnings.py <project-name>
  python scripts/merge-learnings.py <project-name> --domain gaming
  python scripts/merge-learnings.py <project-name> --dry-run
  python scripts/merge-learnings.py <project-name> --domain gaming --dry-run
"""

import argparse
import glob
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("오류: pyyaml이 설치되지 않았습니다. pip install pyyaml 실행 후 재시도하세요.")
    sys.exit(1)


# ============================================================
# 상수
# ============================================================

# Division 학습 파일이 존재할 수 있는 이름 목록
DIVISION_NAMES = [
    "market", "product", "capability", "finance",
    "people-org", "operations", "regulatory",
]

# 카테고리별 매칭 키 필드 (유사도 판정용)
CATEGORY_KEY_FIELD = {
    "sources": "name",
    "frameworks": "name",
    "patterns": "id",
    "terms": "term",
    "pitfalls": "id",
}

# 카테고리별 도메인 지식 파일명
CATEGORY_FILE = {
    "sources": "learned-sources.yaml",
    "frameworks": "learned-frameworks.yaml",
    "patterns": "learned-patterns.yaml",
    "terms": "learned-terms.yaml",
    "pitfalls": "learned-pitfalls.yaml",
}

# 성숙도 판정 기준
MATURITY_THRESHOLDS = {
    0: "empty",
    1: "nascent",
    3: "developing",
    6: "mature",
}


# ============================================================
# 데이터 클래스
# ============================================================

@dataclass
class MergeStats:
    """머지 결과 통계"""
    added: int = 0
    updated: int = 0
    conflicts: int = 0
    skipped: int = 0

    def total(self):
        return self.added + self.updated + self.conflicts


@dataclass
class MergeReport:
    """전체 머지 보고서"""
    project: str
    domain: str
    divisions_processed: List[str] = field(default_factory=list)
    category_stats: Dict[str, MergeStats] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    dry_run: bool = False


# ============================================================
# 유틸리티
# ============================================================

def findProjectRoot():
    """스크립트 위치 기준으로 프로젝트 루트 반환"""
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(scriptDir)


def loadYaml(filepath):
    """YAML 파일 로드. 파일 없으면 None 반환"""
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def saveYaml(filepath, data):
    """YAML 파일 저장. 디렉토리 자동 생성"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )


def extractDomainFromBrief(briefPath):
    """00-client-brief.md에서 domain 추출. 없으면 None"""
    if not os.path.exists(briefPath):
        return None
    with open(briefPath, "r", encoding="utf-8") as f:
        content = f.read()
    # domain: xxx 또는 도메인: xxx 패턴 탐색
    match = re.search(r"(?:domain|도메인)\s*[:：]\s*(\S+)", content, re.IGNORECASE)
    if match:
        return match.group(1).strip().strip('"').strip("'")
    return None


def determineMaturity(projectCount):
    """프로젝트 수에 따른 성숙도 판정"""
    if projectCount >= 6:
        return "mature"
    elif projectCount >= 3:
        return "developing"
    elif projectCount >= 1:
        return "nascent"
    return "empty"


# ============================================================
# 머지 엔진
# ============================================================

def findExistingItem(existingItems, newItem, keyField):
    """기존 항목 목록에서 키 필드가 일치하는 항목 탐색. 인덱스와 항목 반환"""
    newKey = newItem.get(keyField)
    if not newKey:
        return -1, None
    for idx, existing in enumerate(existingItems):
        if existing.get(keyField) == newKey:
            return idx, existing
    return -1, None


def mergeItem(existing, new, projectName, keyField):
    """
    단일 항목 머지. 규칙 1(기존 갱신) 또는 규칙 3(충돌) 적용.
    반환: (mergedItem, action) — action은 "updated" | "conflict"
    """
    merged = dict(existing)

    # confirmed_by_projects 배열 관리
    confirmedList = merged.get("confirmed_by_projects", [])
    if not isinstance(confirmedList, list):
        confirmedList = []
    if projectName not in confirmedList:
        confirmedList.append(projectName)
    merged["confirmed_by_projects"] = confirmedList

    # 충돌 감지: reliability/effectiveness/confidence가 다른 방향으로 변경
    conflictDetected = False
    conflictFields = ["reliability", "effectiveness", "confidence", "severity"]
    for cf in conflictFields:
        if cf in new and cf in existing:
            if new[cf] != existing[cf]:
                # 값이 다르면 — 충돌 가능성 검토
                # 같은 프로젝트의 Phase 2 갱신이면 덮어쓰기 (규칙 4)
                if projectName in existing.get("confirmed_by_projects", []):
                    # 규칙 4: 같은 프로젝트 Phase 2 → 덮어쓰기
                    merged[cf] = new[cf]
                else:
                    # 규칙 3: 다른 프로젝트 → 충돌 기록
                    conflictDetected = True
                    conflictEntry = {
                        "field": cf,
                        "existing_value": existing[cf],
                        "new_value": new[cf],
                        "from_project": projectName,
                        "detected_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        "status": "needs_verification",
                    }
                    if "conflicts" not in merged:
                        merged["conflicts"] = []
                    merged["conflicts"].append(conflictEntry)

    # notes 보강: 새로운 notes가 있으면 기존에 추가
    if "notes" in new and new["notes"]:
        existingNotes = merged.get("notes", "")
        newNotes = new["notes"]
        if existingNotes and newNotes not in existingNotes:
            merged["notes"] = f"{existingNotes} | [{projectName}] {newNotes}"
        elif not existingNotes:
            merged["notes"] = newNotes

    # 규칙 4: 같은 프로젝트 Phase 2 → 비충돌 필드 덮어쓰기
    if projectName in existing.get("confirmed_by_projects", []):
        for k, v in new.items():
            if k == keyField or k == "confirmed_by_projects" or k == "first_learned":
                continue  # 키 필드, 이력 필드는 보존
            if k == "notes":
                continue  # notes는 위에서 별도 처리
            if k in conflictFields:
                merged[k] = v  # 규칙 4: 덮어쓰기
            elif k not in merged or merged[k] != v:
                merged[k] = v

    action = "conflict" if conflictDetected else "updated"
    return merged, action


def createNewItem(item, projectName):
    """규칙 2: 신규 항목 생성. first_learned 및 confirmed_by_projects 설정"""
    newItem = dict(item)
    newItem["first_learned"] = projectName
    newItem["confirmed_by_projects"] = [projectName]
    return newItem


def mergeCategory(existingItems, newItems, projectName, keyField):
    """
    단일 카테고리의 전체 항목을 머지.
    반환: (mergedList, MergeStats)
    """
    stats = MergeStats()
    mergedList = list(existingItems)  # 기존 항목 복사

    for newItem in newItems:
        idx, existingItem = findExistingItem(mergedList, newItem, keyField)

        if existingItem is not None:
            # 규칙 1 또는 3: 기존 항목 갱신/충돌
            merged, action = mergeItem(existingItem, newItem, projectName, keyField)
            mergedList[idx] = merged
            if action == "conflict":
                stats.conflicts += 1
            else:
                stats.updated += 1
        else:
            # 규칙 2: 신규 항목
            newEntry = createNewItem(newItem, projectName)
            mergedList.append(newEntry)
            stats.added += 1

    return mergedList, stats


# ============================================================
# 도메인 지식 파일 로드/저장
# ============================================================

def loadDomainKnowledge(domainDir, category):
    """도메인 knowledge 파일에서 항목 리스트 로드"""
    filepath = os.path.join(domainDir, CATEGORY_FILE[category])
    data = loadYaml(filepath)
    if data is None:
        return []
    return data.get(category, []) or []


def saveDomainKnowledge(domainDir, category, items, domainName):
    """도메인 knowledge 파일에 머지된 항목 저장"""
    filepath = os.path.join(domainDir, CATEGORY_FILE[category])
    existingData = loadYaml(filepath) or {}

    # 기존 파일 구조 유지하면서 항목 리스트만 교체
    existingData[category] = items

    # _meta 섹션이 있으면 유지
    if "_meta" not in existingData:
        existingData["_meta"] = {
            "domain": domainName,
            "last_updated": None,
            "projects_seen": [],
        }

    saveYaml(filepath, existingData)


def updateMetaYaml(domainDir, domainName, projectName, categoryCounts):
    """규칙 5: _meta.yaml 갱신"""
    metaPath = os.path.join(domainDir, "_meta.yaml")
    meta = loadYaml(metaPath) or {}

    # 기본 구조 보장
    if "knowledge_status" not in meta:
        meta["knowledge_status"] = {}
    ks = meta["knowledge_status"]

    # projects_seen 갱신 (중복 방지)
    projectsSeen = ks.get("projects_seen", []) or []
    if projectName not in projectsSeen:
        projectsSeen.append(projectName)
    ks["projects_seen"] = projectsSeen

    # last_project, last_updated 갱신
    ks["last_project"] = projectName
    ks["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # counts 갱신
    ks["counts"] = categoryCounts

    meta["knowledge_status"] = ks

    # maturity 재판정
    meta["maturity"] = determineMaturity(len(projectsSeen))

    # domain 정보 보존
    if "domain" not in meta:
        meta["domain"] = domainName

    saveYaml(metaPath, meta)
    return meta


# ============================================================
# 검증
# ============================================================

def validateMergeResult(domainDir, categoryCounts, report):
    """머지 후 검증: 중복 확인, 스키마 준수, 카운트 일치"""
    errors = []

    for category, keyField in CATEGORY_KEY_FIELD.items():
        items = loadDomainKnowledge(domainDir, category)
        actualCount = len(items)

        # 1. 중복 확인
        keys = []
        for item in items:
            key = item.get(keyField)
            if key:
                keys.append(key)
        duplicates = [k for k in set(keys) if keys.count(k) > 1]
        if duplicates:
            errors.append(f"[{category}] 중복 항목 발견: {duplicates}")

        # 2. 스키마 준수 — 필수 필드 확인
        requiredFields = {
            "sources": ["name", "reliability"],
            "frameworks": ["name", "effectiveness"],
            "patterns": ["id", "pattern"],
            "terms": ["term", "definition"],
            "pitfalls": ["id", "pitfall"],  # pitfalls는 id 필수이나 learnings 입력에 없을 수 있음
        }
        for idx, item in enumerate(items):
            # pitfalls의 id는 자동 생성될 수 있으므로 유연하게 처리
            for rf in requiredFields.get(category, []):
                if rf not in item or not item[rf]:
                    # pitfall의 id 누락은 경고만
                    if category == "pitfalls" and rf == "id":
                        continue
                    errors.append(
                        f"[{category}][{idx}] 필수 필드 누락: {rf}"
                    )

        # 3. 카운트 일치
        if categoryCounts.get(category, 0) != actualCount:
            errors.append(
                f"[{category}] 카운트 불일치: _meta={categoryCounts.get(category, 0)}, 실제={actualCount}"
            )

    report.validation_errors = errors
    return len(errors) == 0


# ============================================================
# 핵심 실행 로직
# ============================================================

def mergeLearningsForProject(projectDir, domainDir, domainName, projectName, dryRun=False):
    """프로젝트의 모든 Division 학습을 도메인 지식에 머지"""
    report = MergeReport(project=projectName, domain=domainName, dry_run=dryRun)
    learningsDir = os.path.join(projectDir, "learnings")

    if not os.path.isdir(learningsDir):
        print(f"경고: 학습 디렉토리가 없습니다: {learningsDir}")
        return report

    # 학습 파일 탐색 (패턴: {division}-learnings.yaml)
    learningFiles = glob.glob(os.path.join(learningsDir, "*-learnings.yaml"))
    if not learningFiles:
        print(f"경고: 학습 파일이 없습니다: {learningsDir}/*-learnings.yaml")
        return report

    # 카테고리별 누적 통계
    for category in CATEGORY_KEY_FIELD:
        report.category_stats[category] = MergeStats()

    # 각 Division 학습 파일 처리
    for learningFile in sorted(learningFiles):
        divisionName = os.path.basename(learningFile).replace("-learnings.yaml", "")
        data = loadYaml(learningFile)
        if not data:
            print(f"  스킵: {learningFile} (비어있음)")
            continue

        report.divisions_processed.append(divisionName)
        learnings = data.get("learnings", {})
        if not learnings:
            print(f"  스킵: {learningFile} (learnings 섹션 없음)")
            continue

        fileProjectName = data.get("project", projectName)

        print(f"  처리 중: {divisionName} ({os.path.basename(learningFile)})")

        # 카테고리별 머지
        for category, keyField in CATEGORY_KEY_FIELD.items():
            newItems = learnings.get(category, [])
            if not newItems:
                continue

            # pitfalls에 id가 없는 항목은 자동 생성
            if category == "pitfalls":
                existingPitfalls = loadDomainKnowledge(domainDir, category)
                maxNum = 0
                for p in existingPitfalls:
                    pid = p.get("id", "")
                    match = re.search(r"(\d+)$", pid)
                    if match:
                        maxNum = max(maxNum, int(match.group(1)))
                for item in newItems:
                    if "id" not in item or not item["id"]:
                        maxNum += 1
                        item["id"] = f"PF-{maxNum:03d}"

            # 기존 도메인 지식 로드
            existingItems = loadDomainKnowledge(domainDir, category)

            # 머지 실행
            mergedItems, stats = mergeCategory(
                existingItems, newItems, fileProjectName, keyField
            )

            # 통계 누적
            report.category_stats[category].added += stats.added
            report.category_stats[category].updated += stats.updated
            report.category_stats[category].conflicts += stats.conflicts

            # dry-run이 아닐 때만 저장
            if not dryRun:
                saveDomainKnowledge(domainDir, category, mergedItems, domainName)
            else:
                # dry-run: 변경 사항 상세 출력
                if stats.total() > 0:
                    print(f"    [{category}] 추가={stats.added}, 갱신={stats.updated}, 충돌={stats.conflicts}")
                    for item in newItems:
                        key = item.get(keyField, "(키 없음)")
                        idx, existing = findExistingItem(existingItems, item, keyField)
                        if existing:
                            print(f"      ↻ 갱신: {key}")
                        else:
                            print(f"      + 신규: {key}")

    # _meta.yaml 갱신
    categoryCounts = {}
    for category in CATEGORY_KEY_FIELD:
        if dryRun:
            # dry-run: 현재 항목 수 + 추가 예정 수
            existing = loadDomainKnowledge(domainDir, category)
            categoryCounts[category] = len(existing) + report.category_stats[category].added
        else:
            items = loadDomainKnowledge(domainDir, category)
            categoryCounts[category] = len(items)

    if not dryRun:
        updateMetaYaml(domainDir, domainName, projectName, categoryCounts)

    # 검증 (dry-run이 아닐 때만)
    if not dryRun:
        validateMergeResult(domainDir, categoryCounts, report)

    return report


# ============================================================
# 출력
# ============================================================

def printReport(report):
    """머지 결과 요약 출력"""
    modeLabel = "[DRY-RUN] " if report.dry_run else ""
    print(f"\n{'=' * 60}")
    print(f"{modeLabel}머지 결과 요약")
    print(f"{'=' * 60}")
    print(f"프로젝트: {report.project}")
    print(f"도메인:   {report.domain}")
    print(f"처리 Division: {', '.join(report.divisions_processed) if report.divisions_processed else '(없음)'}")
    print()

    totalAdded = 0
    totalUpdated = 0
    totalConflicts = 0

    print(f"{'카테고리':<15} {'추가':>6} {'갱신':>6} {'충돌':>6}")
    print(f"{'-' * 15} {'-' * 6} {'-' * 6} {'-' * 6}")
    for category, stats in report.category_stats.items():
        if stats.total() > 0 or True:  # 모든 카테고리 표시
            print(f"{category:<15} {stats.added:>6} {stats.updated:>6} {stats.conflicts:>6}")
            totalAdded += stats.added
            totalUpdated += stats.updated
            totalConflicts += stats.conflicts

    print(f"{'-' * 15} {'-' * 6} {'-' * 6} {'-' * 6}")
    print(f"{'합계':<15} {totalAdded:>6} {totalUpdated:>6} {totalConflicts:>6}")

    # 검증 결과
    if report.validation_errors:
        print(f"\n검증 오류 ({len(report.validation_errors)}건):")
        for err in report.validation_errors:
            print(f"  ✗ {err}")
    elif not report.dry_run and report.divisions_processed:
        print(f"\n검증: 통과")

    print(f"{'=' * 60}")


# ============================================================
# CLI
# ============================================================

def buildParser():
    """argparse 파서 구성"""
    parser = argparse.ArgumentParser(
        description="프로젝트 학습 결과를 도메인 지식 베이스에 머지",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python scripts/merge-learnings.py my-project
  python scripts/merge-learnings.py my-project --domain gaming
  python scripts/merge-learnings.py my-project --dry-run
        """,
    )
    parser.add_argument(
        "project",
        help="프로젝트 디렉토리명",
    )
    parser.add_argument(
        "--domain",
        default=None,
        help="도메인명 (기본값: 프로젝트 brief에서 추출 또는 'example')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 파일 수정 없이 머지 결과만 출력",
    )
    return parser


def main():
    parser = buildParser()
    args = parser.parse_args()

    projectRoot = findProjectRoot()
    projectDir = os.path.join(projectRoot, args.project)

    # 프로젝트 디렉토리 확인
    if not os.path.isdir(projectDir):
        print(f"오류: 프로젝트 디렉토리를 찾을 수 없습니다: {projectDir}")
        sys.exit(1)

    # 도메인 결정
    domainName = args.domain
    if not domainName:
        briefPath = os.path.join(projectDir, "00-client-brief.md")
        domainName = extractDomainFromBrief(briefPath)
    if not domainName:
        domainName = "example"
        print(f"정보: 도메인을 자동 감지하지 못했습니다. 기본값 '{domainName}' 사용")

    domainDir = os.path.join(projectRoot, "domains", domainName, "knowledge")

    # 도메인 knowledge 디렉토리 확인
    if not os.path.isdir(domainDir):
        print(f"오류: 도메인 지식 디렉토리를 찾을 수 없습니다: {domainDir}")
        print(f"  → 'python scripts/merge-learnings.py {args.project} --domain example' 로 시도하거나,")
        print(f"  → 먼저 /setup으로 도메인을 생성하세요.")
        sys.exit(1)

    projectName = args.project

    # 실행
    modeStr = " (dry-run)" if args.dry_run else ""
    print(f"학습 머지 시작: {projectName} → {domainName}{modeStr}")
    print(f"  프로젝트: {projectDir}")
    print(f"  도메인:   {domainDir}")
    print()

    report = mergeLearningsForProject(
        projectDir, domainDir, domainName, projectName, dryRun=args.dry_run
    )

    printReport(report)

    # 종료 코드
    if report.validation_errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
