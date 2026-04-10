#!/usr/bin/env python3
"""
통합 출처 추적 테이블 생성기 (Source Registry Generator)
프로젝트의 source_index + golden-facts + data-registry + 보고서를 통합하여
source-registry.csv를 생성한다.

사용법: python3 scripts/generate-source-registry.py {project-name}
"""
import sys, os, csv, re, glob
import yaml

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/generate-source-registry.py {project-name}")
        sys.exit(1)

    project = sys.argv[1]
    project_dir = os.path.abspath(project)
    if not os.path.isdir(project_dir):
        print(f"Error: {project_dir} not found")
        sys.exit(1)

    # 1. 모든 source_index 수집
    sources = {}  # source_id -> dict
    findings_dir = os.path.join(project_dir, "findings")
    if os.path.isdir(findings_dir):
        for yaml_path in glob.glob(os.path.join(findings_dir, "**/*.yaml"), recursive=True):
            try:
                with open(yaml_path) as f:
                    data = yaml.safe_load(f)
                if not data:
                    continue
                # source_index가 최상위에 있을 수도, 중첩되어 있을 수도 있음
                source_list = data.get("source_index", [])
                if not source_list:
                    continue
                # division 추출 (findings/{division}/... 경로에서)
                rel = os.path.relpath(yaml_path, findings_dir)
                division = rel.split(os.sep)[0] if os.sep in rel else "unknown"
                for src in source_list:
                    sid = src.get("id", "")
                    if sid not in sources:
                        sources[sid] = {
                            "source_id": sid,
                            "name": src.get("name", ""),
                            "type": src.get("type", ""),
                            "url": src.get("url", "") or "",
                            "reliability": src.get("reliability", ""),
                            "accessed": src.get("accessed", ""),
                            "summary": src.get("summary", src.get("note", "")),
                            "division": division,
                            "collected_by": src.get("collected_by", ""),
                            "used_in": "",
                            "claims": "",
                            "golden_facts": "",
                            "verified": src.get("verified", ""),
                            "note": src.get("note", ""),
                        }
            except Exception:
                continue

    # 2. golden-facts.yaml에서 source_id 역참조
    gf_to_sources = {}  # fact_id → [source_id, ...] (보고서 [GF-###] 태그 역참조용)
    gf_path = os.path.join(findings_dir, "golden-facts.yaml")
    if os.path.isfile(gf_path):
        try:
            with open(gf_path) as f:
                gf_data = yaml.safe_load(f)
            facts = gf_data.get("facts", []) if gf_data else []
            for fact in facts:
                fact_id = fact.get("id", "")
                # (a) sources(복수) / source_id(단수) 양쪽 호환
                fact_sources = fact.get("sources", [])
                if not fact_sources and fact.get("source_id"):
                    fact_sources = [fact.get("source_id")]
                # fact_id → source_id 매핑 저장
                gf_to_sources[fact_id] = fact_sources
                for sid in fact_sources:
                    if sid in sources:
                        # (c) golden_facts 필드에 fact_id 추가
                        existing = sources[sid].get("golden_facts", "")
                        if fact_id not in existing:
                            sources[sid]["golden_facts"] = f"{existing}, {fact_id}".strip(", ")
        except Exception:
            pass

    # 3. 보고서에서 [S##] / [GF-###] 참조 파싱
    reports_dir = os.path.join(project_dir, "reports")
    if os.path.isdir(reports_dir):
        for md_path in glob.glob(os.path.join(reports_dir, "*.md")):
            try:
                with open(md_path) as f:
                    content = f.read()
                report_name = os.path.basename(md_path).replace(".md", "")
                # [S01], [S02] 등의 패턴 찾기
                refs = re.findall(r'\[S(\d+)\]', content)
                for ref_num in refs:
                    sid = f"S{ref_num.zfill(2)}"
                    if sid in sources:
                        existing_used = sources[sid].get("used_in", "")
                        if report_name not in existing_used:
                            sources[sid]["used_in"] = f"{existing_used}, {report_name}".strip(", ")
                # (b) [GF-001] 등의 패턴 → source_id 역참조하여 used_in 기록
                gf_refs = re.findall(r'\[GF-(\d{3})\]', content)
                for gf_num in gf_refs:
                    gf_id = f"GF-{gf_num}"
                    for sid in gf_to_sources.get(gf_id, []):
                        if sid in sources:
                            existing_used = sources[sid].get("used_in", "")
                            if report_name not in existing_used:
                                sources[sid]["used_in"] = f"{existing_used}, {report_name}".strip(", ")
            except Exception:
                continue

    # 4. data-registry.csv 보강 (있으면)
    dr_path = os.path.join(project_dir, "data", "data-registry.csv")
    if os.path.isfile(dr_path):
        try:
            with open(dr_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # data-registry의 source 필드가 source_id와 매칭되면 보강
                    src_ref = row.get("source", "")
                    if src_ref in sources and not sources[src_ref].get("collected_by"):
                        sources[src_ref]["collected_by"] = row.get("collected_by", "")
        except Exception:
            pass

    # 5. CSV 출력
    output_path = os.path.join(project_dir, "source-registry.csv")
    fieldnames = [
        "source_id", "name", "type", "url", "reliability", "accessed",
        "summary", "division", "collected_by", "used_in", "claims",
        "golden_facts", "verified", "note"
    ]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for sid in sorted(sources.keys()):
            writer.writerow(sources[sid])

    print(f"✓ source-registry.csv 생성: {output_path}")
    print(f"  총 {len(sources)}개 출처 등록")

    # 통계
    no_url = sum(1 for s in sources.values() if not s["url"])
    no_summary = sum(1 for s in sources.values() if not s["summary"])
    no_used = sum(1 for s in sources.values() if not s["used_in"])
    print(f"  URL 없음: {no_url}개")
    print(f"  요약 없음: {no_summary}개")
    print(f"  미사용: {no_used}개")

if __name__ == "__main__":
    main()
