#!/usr/bin/env python3
"""
리서치 데이터 → 차트 자동 생성.
division-synthesis.yaml, golden-facts.yaml의 수치 데이터를 분석하여
최적 차트 유형을 선택하고 PNG로 렌더링한다.

사용법:
  python scripts/generate-charts.py <project-name>
  python scripts/generate-charts.py <project-name> --division market
  python scripts/generate-charts.py <project-name> --facts-only
  python scripts/generate-charts.py <project-name> --style dark
"""

import sys
import os
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ============================================================
# 의존성 확인
# ============================================================

def checkDependencies():
    """필수 패키지 설치 확인"""
    missing = []
    try:
        import yaml
    except ImportError:
        missing.append("pyyaml")
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")
    if missing:
        print(f"필수 패키지 누락: {', '.join(missing)}")
        print(f"설치: pip install {' '.join(missing)}")
        return False
    return True


# ============================================================
# 데이터 모델
# ============================================================

@dataclass
class ChartData:
    """차트 렌더링에 필요한 데이터 구조"""
    title: str
    chart_type: str = ""  # 자동 선택 전엔 빈 문자열
    labels: list = field(default_factory=list)       # X축 레이블 (범주 또는 시간)
    series: dict = field(default_factory=dict)       # {시리즈명: [값 리스트]}
    unit: str = ""                                    # 단위 (예: "$B", "%", "만 명")
    source_file: str = ""                             # 원본 파일 경로
    related_claims: list = field(default_factory=list) # 관련 Claim ID
    category: str = ""                                # golden-facts category 등
    is_percentage: bool = False                       # 합계가 ~100%인 비율 데이터
    is_timeseries: bool = False                       # 시간축 포함 여부
    is_matrix: bool = False                           # 2차원 매트릭스 여부
    is_scenario: bool = False                         # 시나리오 비교 여부
    is_waterfall: bool = False                        # 분해 구조 여부


@dataclass
class ChartMeta:
    """생성된 차트의 메타데이터"""
    chart_id: str          # CHT-001
    chart_type: str        # line, bar, pie 등
    title: str
    data_source: str       # 원본 파일
    related_claims: list
    file_path: str         # 출력 PNG 경로


# ============================================================
# 데이터 추출기
# ============================================================

class ChartDataExtractor:
    """리서치 산출물에서 차트용 데이터 추출"""

    def __init__(self, projectPath: str):
        self.projectPath = Path(projectPath)

    def extractAll(self, division: Optional[str] = None, factsOnly: bool = False) -> list:
        """모든 소스에서 차트 데이터 추출"""
        charts = []

        # 1. golden-facts.yaml
        factsPath = self.projectPath / "findings" / "golden-facts.yaml"
        if factsPath.exists():
            charts.extend(self.extractFromGoldenFacts(str(factsPath)))

        if factsOnly:
            return charts

        # 2. division-synthesis.yaml 파일들
        if division:
            # 특정 Division만
            synthPath = self.projectPath / "findings" / division / "division-synthesis.yaml"
            if synthPath.exists():
                charts.extend(self.extractFromSynthesis(str(synthPath), division))
        else:
            # 모든 Division
            findingsDir = self.projectPath / "findings"
            if findingsDir.exists():
                for divDir in findingsDir.iterdir():
                    if divDir.is_dir():
                        synthPath = divDir / "division-synthesis.yaml"
                        if synthPath.exists():
                            charts.extend(self.extractFromSynthesis(str(synthPath), divDir.name))

        # 3. report-docs.md
        reportPath = self.projectPath / "reports" / "report-docs.md"
        if reportPath.exists():
            charts.extend(self.extractFromReport(str(reportPath)))

        return charts

    def extractFromGoldenFacts(self, factsPath: str) -> list:
        """golden-facts.yaml에서 시계열/비교 데이터 추출"""
        import yaml

        try:
            with open(factsPath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"  [경고] golden-facts.yaml 파싱 실패: {e}")
            return []

        if not data or 'facts' not in data:
            return []

        facts = data['facts']
        charts = []

        # category별 그룹핑
        groups = {}
        for fact in facts:
            cat = fact.get('category', 'unknown')
            if cat not in groups:
                groups[cat] = []
            groups[cat].append(fact)

        for cat, factList in groups.items():
            # 같은 entity+metric의 시계열 데이터 탐지
            timeseriesGroups = self._groupTimeseries(factList)
            for tsKey, tsFacts in timeseriesGroups.items():
                if len(tsFacts) >= 2:
                    # 시계열 데이터 → 꺾은선 차트
                    chartData = self._buildTimeseriesChart(tsKey, tsFacts, cat, factsPath)
                    if chartData:
                        charts.append(chartData)

            # 같은 metric, 다른 entity → 비교 차트
            compGroups = self._groupComparison(factList)
            for compKey, compFacts in compGroups.items():
                if len(compFacts) >= 2:
                    chartData = self._buildComparisonChart(compKey, compFacts, cat, factsPath)
                    if chartData:
                        charts.append(chartData)

        return charts

    def _groupTimeseries(self, facts: list) -> dict:
        """같은 entity+metric인데 as_of가 다른 것들을 그룹핑"""
        groups = {}
        for f in facts:
            entity = f.get('entity', '')
            metric = f.get('metric', '')
            asOf = f.get('as_of', '')
            if entity and metric and asOf:
                key = f"{entity}|{metric}"
                if key not in groups:
                    groups[key] = []
                groups[key].append(f)
        return groups

    def _groupComparison(self, facts: list) -> dict:
        """같은 metric인데 entity가 다른 것들을 그룹핑"""
        groups = {}
        for f in facts:
            metric = f.get('metric', '')
            asOf = f.get('as_of', '')
            if metric:
                key = f"{metric}|{asOf}" if asOf else metric
                if key not in groups:
                    groups[key] = []
                groups[key].append(f)
        # entity가 모두 같은 그룹은 비교 차트 대상 아님
        filtered = {}
        for k, v in groups.items():
            entities = set(f.get('entity', '') for f in v)
            if len(entities) >= 2:
                filtered[k] = v
        return filtered

    def _buildTimeseriesChart(self, key: str, facts: list, category: str, sourcePath: str) -> Optional[ChartData]:
        """시계열 팩트 → ChartData 변환"""
        entity, metric = key.split('|', 1)
        # as_of 기준 정렬
        sortedFacts = sorted(facts, key=lambda f: str(f.get('as_of', '')))
        labels = [str(f.get('as_of', '')) for f in sortedFacts]
        values = []
        for f in sortedFacts:
            val = self._parseNumericValue(f.get('value'))
            if val is None:
                return None
            values.append(val)

        unit = sortedFacts[0].get('unit', '')
        claimIds = [f.get('id', '') for f in sortedFacts]

        return ChartData(
            title=f"{entity} {metric} 추이",
            labels=labels,
            series={metric: values},
            unit=unit,
            source_file=sourcePath,
            related_claims=claimIds,
            category=category,
            is_timeseries=True,
        )

    def _buildComparisonChart(self, key: str, facts: list, category: str, sourcePath: str) -> Optional[ChartData]:
        """비교 팩트 → ChartData 변환"""
        labels = []
        values = []
        for f in facts:
            entity = f.get('entity', '알 수 없음')
            val = self._parseNumericValue(f.get('value'))
            if val is None:
                continue
            labels.append(entity)
            values.append(val)

        if len(labels) < 2:
            return None

        metric = key.split('|')[0]
        unit = facts[0].get('unit', '')
        claimIds = [f.get('id', '') for f in facts]

        # 비율 데이터 감지 (합계 ~100%)
        total = sum(values)
        isPct = 95 <= total <= 105 and unit in ['%', '퍼센트', 'percent']

        return ChartData(
            title=f"{metric} 비교",
            labels=labels,
            series={metric: values},
            unit=unit,
            source_file=sourcePath,
            related_claims=claimIds,
            category=category,
            is_percentage=isPct,
        )

    def extractFromSynthesis(self, synthPath: str, divisionName: str) -> list:
        """division-synthesis.yaml에서 수치 테이블 추출"""
        import yaml

        try:
            with open(synthPath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"  [경고] {synthPath} 파싱 실패: {e}")
            return []

        if not data:
            return []

        charts = []

        # triangulation 데이터 → 비교 차트
        synth = data.get('synthesis', {})
        if synth:
            triangulations = synth.get('triangulation', [])
            for tri in triangulations:
                chartData = self._buildTriangulationChart(tri, synthPath, divisionName)
                if chartData:
                    charts.append(chartData)

            # matrix highlights → 히트맵 또는 그룹 막대 후보
            matrix = synth.get('matrix', {})
            if matrix:
                for matrixKey, matrixData in matrix.items():
                    if isinstance(matrixData, dict) and 'highlights' in matrixData:
                        chartData = self._buildMatrixChart(matrixKey, matrixData, synthPath, divisionName)
                        if chartData:
                            charts.append(chartData)

        # claims에서 시나리오 데이터 탐지
        claims = data.get('claims', [])
        scenarioData = self._detectScenarioClaims(claims, synthPath)
        if scenarioData:
            charts.append(scenarioData)

        # confidence_summary → 파이 차트
        divSummary = data.get('division_summary', {})
        if divSummary:
            confSummary = divSummary.get('confidence_summary', {})
            if confSummary:
                chartData = self._buildConfidenceChart(confSummary, synthPath, divisionName)
                if chartData:
                    charts.append(chartData)

        return charts

    def _buildTriangulationChart(self, tri: dict, sourcePath: str, division: str) -> Optional[ChartData]:
        """삼각 검증 데이터 → 비교 차트"""
        metric = tri.get('metric', '')
        vals = tri.get('values', [])
        if len(vals) < 2:
            return None

        labels = []
        values = []
        for v in vals:
            agent = v.get('agent', '')
            valStr = v.get('value', '')
            numVal = self._parseNumericValue(valStr)
            if numVal is not None:
                labels.append(agent)
                values.append(numVal)

        if len(labels) < 2:
            return None

        return ChartData(
            title=f"[{division}] {metric} — 삼각 검증",
            labels=labels,
            series={metric: values},
            source_file=sourcePath,
            is_timeseries=False,
        )

    def _buildMatrixChart(self, matrixKey: str, matrixData: dict, sourcePath: str, division: str) -> Optional[ChartData]:
        """매트릭스 highlights에서 수치를 추출하여 그룹 막대 차트 구성"""
        highlights = matrixData.get('highlights', [])
        if len(highlights) < 2:
            return None

        labels = []
        values = []
        for h in highlights:
            cell = h.get('cell', '')
            finding = h.get('finding', '')
            # finding에서 첫 번째 수치 추출
            numVal = self._extractFirstNumber(finding)
            if numVal is not None and cell:
                labels.append(cell)
                values.append(numVal)

        if len(labels) < 2:
            return None

        return ChartData(
            title=f"[{division}] {matrixKey} 매트릭스",
            labels=labels,
            series={"수치": values},
            source_file=sourcePath,
            is_matrix=True,
        )

    def _detectScenarioClaims(self, claims: list, sourcePath: str) -> Optional[ChartData]:
        """Claims에서 BASE/UPSIDE/DOWNSIDE 시나리오 패턴 감지"""
        scenarioPatterns = ['BASE', 'UPSIDE', 'DOWNSIDE', 'BEAR', 'BULL']
        scenarioLabels = []
        scenarioValues = []

        # 시나리오별로 대표 값 1개만 수집 (중복 방지)
        scenarioFound = {}  # {패턴: (값, claim_id)}
        for claim in claims:
            claimText = claim.get('claim', '')
            claimId = claim.get('id', '')
            for pattern in scenarioPatterns:
                if pattern in claimText.upper() and pattern not in scenarioFound:
                    # 해당 패턴 근처의 수치 추출
                    # 예: "BASE 첫해 $40M", "UPSIDE $90M"
                    regex = rf'{pattern}\s*[^$]*\$(\d+[\d,.]*)[MBK]?'
                    match = re.search(regex, claimText, re.IGNORECASE)
                    if match:
                        val = float(match.group(1).replace(',', ''))
                        scenarioFound[pattern] = (val, claimId)

        for pattern in scenarioPatterns:
            if pattern in scenarioFound:
                scenarioLabels.append(pattern)
                scenarioValues.append(scenarioFound[pattern][0])

        if len(scenarioLabels) >= 2:
            return ChartData(
                title="시나리오별 매출 전망",
                labels=scenarioLabels,
                series={"매출": scenarioValues},
                unit="$M",
                source_file=sourcePath,
                is_scenario=True,
            )
        return None

    def _buildConfidenceChart(self, confSummary: dict, sourcePath: str, division: str) -> Optional[ChartData]:
        """confidence_summary → 파이/도넛 차트"""
        labels = []
        values = []
        for level in ['high', 'medium', 'low', 'unverified']:
            rawVal = confSummary.get(level, 0)
            # "2건" 같은 문자열 처리
            if isinstance(rawVal, str):
                numMatch = re.search(r'(\d+)', rawVal)
                if numMatch:
                    rawVal = int(numMatch.group(1))
                else:
                    rawVal = 0
            if rawVal and rawVal > 0:
                levelKo = {'high': '확정(High)', 'medium': '유력(Medium)',
                           'low': '가정(Low)', 'unverified': '미확인'}
                labels.append(levelKo.get(level, level))
                values.append(rawVal)

        if len(labels) < 2:
            return None

        return ChartData(
            title=f"[{division}] Claim 확신도 분포",
            labels=labels,
            series={"건수": values},
            unit="건",
            source_file=sourcePath,
            is_percentage=True,  # 구성 비율 → 파이 차트
        )

    def extractFromReport(self, reportPath: str) -> list:
        """report-docs.md에서 마크다운 테이블 추출 → 차트 데이터"""
        try:
            with open(reportPath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  [경고] report-docs.md 읽기 실패: {e}")
            return []

        charts = []
        tables = self._parseMarkdownTables(content)

        for tbl in tables:
            chartData = self._tableToChartData(tbl, reportPath)
            if chartData:
                charts.append(chartData)

        return charts

    def _parseMarkdownTables(self, content: str) -> list:
        """마크다운 테이블을 파싱하여 리스트 반환"""
        tables = []
        # 테이블 패턴: | 로 시작하는 연속 행
        tablePattern = r'((?:^[ \t]*\|.+\|[ \t]*\n){3,})'
        matches = re.findall(tablePattern, content, re.MULTILINE)

        for match in matches:
            rows = [r.strip() for r in match.strip().split('\n') if r.strip()]
            if len(rows) < 3:  # 헤더 + 구분선 + 최소 1행
                continue

            # 헤더 파싱
            headerCells = [c.strip() for c in rows[0].split('|') if c.strip()]
            # 구분선 건너뛰기 (|---|---|)
            if re.match(r'^[\s|:-]+$', rows[1]):
                dataRows = rows[2:]
            else:
                dataRows = rows[1:]

            # 컨텍스트 (테이블 바로 위 헤더)
            tableIdx = content.find(match)
            precedingText = content[:tableIdx]
            headerMatch = re.findall(r'^#{1,4}\s+(.+)$', precedingText, re.MULTILINE)
            contextTitle = headerMatch[-1].strip() if headerMatch else ""

            parsedRows = []
            for row in dataRows:
                cells = [c.strip() for c in row.split('|') if c.strip()]
                if cells:
                    parsedRows.append(cells)

            tables.append({
                'headers': headerCells,
                'rows': parsedRows,
                'context': contextTitle,
            })

        return tables

    def _tableToChartData(self, table: dict, sourcePath: str) -> Optional[ChartData]:
        """파싱된 테이블 → ChartData 변환 (수치 컬럼 감지)"""
        headers = table['headers']
        rows = table['rows']
        context = table['context']

        if len(headers) < 2 or len(rows) < 2:
            return None

        # 수치 컬럼 탐지: 각 컬럼에서 숫자가 50%+ 있으면 수치 컬럼
        numericCols = []
        for colIdx in range(len(headers)):
            numCount = 0
            for row in rows:
                if colIdx < len(row):
                    val = self._parseNumericValue(row[colIdx])
                    if val is not None:
                        numCount += 1
            if numCount >= len(rows) * 0.5 and numCount >= 2:
                numericCols.append(colIdx)

        if not numericCols:
            return None

        # 첫 번째 비수치 컬럼을 레이블로 사용
        labelCol = 0
        for i in range(len(headers)):
            if i not in numericCols:
                labelCol = i
                break

        labels = []
        series = {}
        for colIdx in numericCols:
            series[headers[colIdx]] = []

        for row in rows:
            if labelCol < len(row):
                labels.append(row[labelCol])
            else:
                labels.append("")
            for colIdx in numericCols:
                if colIdx < len(row):
                    val = self._parseNumericValue(row[colIdx])
                    series[headers[colIdx]].append(val if val is not None else 0)
                else:
                    series[headers[colIdx]].append(0)

        # 시간축 감지
        isTs = all(self._isYearLike(l) for l in labels if l)

        return ChartData(
            title=context if context else f"테이블 차트 ({headers[labelCol]})",
            labels=labels,
            series=series,
            source_file=sourcePath,
            is_timeseries=isTs,
        )

    # ── 유틸리티 ──

    def _parseNumericValue(self, valStr) -> Optional[float]:
        """다양한 포맷의 수치를 float으로 파싱"""
        if valStr is None:
            return None
        if isinstance(valStr, (int, float)):
            return float(valStr)

        s = str(valStr).strip()
        if not s:
            return None

        # "$56.9B", "$10.0B", "1,210억원", "28%", "$40M" 등 처리
        # 퍼센트 기호 제거
        s = s.replace('%', '').replace('％', '')
        # 쉼표 제거
        s = s.replace(',', '')
        # 한국어 단위 처리
        koreanUnits = {'억': 1e8, '만': 1e4, '조': 1e12, '천': 1e3}
        for unit, multiplier in koreanUnits.items():
            if unit in s:
                numMatch = re.search(r'[-+]?[\d.]+', s.split(unit)[0])
                if numMatch:
                    return float(numMatch.group()) * multiplier
                return None

        # 영문 단위: $56.9B, $40M, $2.5K
        engUnits = {'B': 1e9, 'b': 1e9, 'M': 1e6, 'm': 1e6, 'K': 1e3, 'k': 1e3, 'T': 1e12}
        # "$56.9B" → 56.9 * 1e9
        engMatch = re.search(r'[-+]?\$?([\d.]+)\s*([BMKTbmkt])\b', s)
        if engMatch:
            num = float(engMatch.group(1))
            unit = engMatch.group(2)
            return num * engUnits.get(unit, 1)

        # 순수 숫자
        numMatch = re.search(r'[-+]?[\d.]+', s)
        if numMatch:
            try:
                return float(numMatch.group())
            except ValueError:
                return None
        return None

    def _extractFirstNumber(self, text: str) -> Optional[float]:
        """문자열에서 첫 번째 의미 있는 숫자(단위 포함) 추출"""
        if not text:
            return None
        # $XX.XB/M 패턴 우선
        dollarMatch = re.search(r'\$([\d.]+)\s*([BMK])', text)
        if dollarMatch:
            num = float(dollarMatch.group(1))
            unit = dollarMatch.group(2)
            multiplier = {'B': 1e9, 'M': 1e6, 'K': 1e3}.get(unit, 1)
            return num * multiplier
        # 퍼센트
        pctMatch = re.search(r'([\d.]+)\s*%', text)
        if pctMatch:
            return float(pctMatch.group(1))
        return None

    def _isYearLike(self, label: str) -> bool:
        """레이블이 연도 형식인지 확인"""
        return bool(re.match(r'^(19|20)\d{2}', str(label).strip()))


# ============================================================
# 차트 유형 선택기
# ============================================================

class ChartTypeSelector:
    """데이터 패턴 분석 → 최적 차트 유형 선택"""

    def select(self, data: ChartData) -> str:
        """
        규칙 기반 차트 유형 선택:
        - 시간축 + 수치 1~3개 → line (꺾은선)
        - 시간축 + 수치 4개+ → grouped_bar (그룹 막대)
        - 비율 합계 ~100% → pie (파이/도넛)
        - 범주 비교 + 수치 1개 → bar (막대)
        - 범주 비교 + 수치 2개+ → grouped_bar
        - 2차원 매트릭스 → heatmap (히트맵)
        - 시나리오 (BASE/UPSIDE/DOWNSIDE) → scenario_bar
        - 분해 구조 → waterfall
        """
        numSeries = len(data.series)

        # 명시적 플래그 체크
        if data.is_waterfall:
            return 'waterfall'
        if data.is_scenario:
            return 'scenario_bar'
        if data.is_matrix and numSeries >= 2:
            return 'heatmap'
        if data.is_percentage:
            return 'pie'

        # 시간축 기반
        if data.is_timeseries:
            return 'line' if numSeries <= 3 else 'grouped_bar'

        # 범주 비교
        if numSeries == 1:
            return 'bar'
        return 'grouped_bar'


# ============================================================
# 차트 렌더러 (matplotlib 기반)
# ============================================================

class ChartRenderer:
    """차트 렌더링 엔진 — 컨설팅 보고서 스타일"""

    # 스타일 프리셋
    STYLES = {
        'consulting': {
            'colors': ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#44BBA4',
                        '#5D6D7E', '#AF7AC5', '#F39C12', '#1ABC9C'],
            'background': '#FFFFFF',
            'grid_alpha': 0.3,
            'title_size': 14,
            'label_size': 10,
            'value_size': 9,
            'figsize': (10, 6),
            'dpi': 150,
        },
        'minimal': {
            'colors': ['#333333', '#666666', '#999999', '#BBBBBB', '#DDDDDD', '#444444'],
            'background': '#FFFFFF',
            'grid_alpha': 0.15,
            'title_size': 13,
            'label_size': 10,
            'value_size': 9,
            'figsize': (10, 6),
            'dpi': 150,
        },
        'dark': {
            'colors': ['#00D2FF', '#FF6B6B', '#FFC857', '#4ECDC4', '#A8E6CF', '#FF8A5C'],
            'background': '#1E1E2E',
            'grid_alpha': 0.2,
            'title_size': 14,
            'label_size': 10,
            'value_size': 9,
            'figsize': (10, 6),
            'dpi': 150,
        },
    }

    def __init__(self, styleName: str = 'consulting'):
        self.style = self.STYLES.get(styleName, self.STYLES['consulting'])
        self._setupFont()

    def _setupFont(self):
        """한국어 폰트 설정 — Pretendard → AppleGothic → sans-serif 폴백"""
        import matplotlib
        import matplotlib.font_manager as fm

        # 사용 가능한 폰트 탐색
        fontCandidates = ['Pretendard', 'AppleGothic', 'Malgun Gothic',
                          'NanumGothic', 'Apple SD Gothic Neo']
        availableFonts = [f.name for f in fm.fontManager.ttflist]

        selectedFont = 'sans-serif'
        for candidate in fontCandidates:
            if candidate in availableFonts:
                selectedFont = candidate
                break

        matplotlib.rcParams['font.family'] = selectedFont
        matplotlib.rcParams['axes.unicode_minus'] = False  # 마이너스 부호 깨짐 방지

    def render(self, data: ChartData, outputPath: str):
        """차트 유형에 따라 적절한 렌더러 호출"""
        renderers = {
            'line': self.renderLine,
            'bar': self.renderBar,
            'grouped_bar': self.renderGroupedBar,
            'pie': self.renderPie,
            'heatmap': self.renderHeatmap,
            'waterfall': self.renderWaterfall,
            'scenario_bar': self.renderScenarioBar,
        }
        renderer = renderers.get(data.chart_type, self.renderBar)
        renderer(data, outputPath)

    def _applyBaseStyle(self, fig, ax):
        """기본 스타일 적용"""
        fig.set_facecolor(self.style['background'])
        ax.set_facecolor(self.style['background'])
        ax.grid(True, alpha=self.style['grid_alpha'], linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # scientific notation 제거 — 읽기 쉬운 포맷 사용
        ax.ticklabel_format(style='plain', axis='both')

        # dark 모드 텍스트 색상
        if self.style['background'] != '#FFFFFF':
            ax.tick_params(colors='#CCCCCC')
            ax.xaxis.label.set_color('#CCCCCC')
            ax.yaxis.label.set_color('#CCCCCC')
            ax.title.set_color('#EEEEEE')
            for spine in ax.spines.values():
                spine.set_color('#555555')

    def renderLine(self, data: ChartData, outputPath: str):
        """꺾은선 차트 — 시계열 추이"""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=self.style['figsize'])
        self._applyBaseStyle(fig, ax)
        colors = self.style['colors']

        for i, (seriesName, values) in enumerate(data.series.items()):
            color = colors[i % len(colors)]
            ax.plot(data.labels, values, marker='o', linewidth=2.5,
                    markersize=6, color=color, label=seriesName)
            # 데이터 레이블
            for x, y in zip(data.labels, values):
                ax.annotate(self._formatValue(y, data.unit),
                           (x, y), textcoords="offset points",
                           xytext=(0, 10), ha='center',
                           fontsize=self.style['value_size'], color=color)

        ax.set_title(data.title, fontsize=self.style['title_size'],
                     fontweight='bold', pad=15)
        if data.unit:
            ax.set_ylabel(data.unit, fontsize=self.style['label_size'])
        if len(data.series) > 1:
            ax.legend(fontsize=self.style['label_size'])
        plt.xticks(rotation=45 if len(data.labels) > 6 else 0,
                   fontsize=self.style['label_size'])
        plt.tight_layout()
        fig.savefig(outputPath, dpi=self.style['dpi'],
                    facecolor=fig.get_facecolor(), bbox_inches='tight')
        plt.close(fig)

    def renderBar(self, data: ChartData, outputPath: str):
        """막대 차트 — 범주 비교"""
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=self.style['figsize'])
        self._applyBaseStyle(fig, ax)
        colors = self.style['colors']

        seriesName = list(data.series.keys())[0]
        values = data.series[seriesName]
        barColors = [colors[i % len(colors)] for i in range(len(values))]

        # 수평 막대 (레이블이 길 때)
        maxLabelLen = max(len(str(l)) for l in data.labels) if data.labels else 0
        if maxLabelLen > 15:
            bars = ax.barh(data.labels, values, color=barColors, height=0.6)
            # 값 레이블
            for bar, val in zip(bars, values):
                ax.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height() / 2,
                        self._formatValue(val, data.unit),
                        va='center', fontsize=self.style['value_size'])
            ax.invert_yaxis()
        else:
            x = np.arange(len(data.labels))
            bars = ax.bar(x, values, color=barColors, width=0.6)
            ax.set_xticks(x)
            ax.set_xticklabels(data.labels, rotation=45 if maxLabelLen > 8 else 0,
                               ha='right' if maxLabelLen > 8 else 'center',
                               fontsize=self.style['label_size'])
            # 값 레이블
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        self._formatValue(val, data.unit),
                        ha='center', va='bottom',
                        fontsize=self.style['value_size'])

        ax.set_title(data.title, fontsize=self.style['title_size'],
                     fontweight='bold', pad=15)
        plt.tight_layout()
        fig.savefig(outputPath, dpi=self.style['dpi'],
                    facecolor=fig.get_facecolor(), bbox_inches='tight')
        plt.close(fig)

    def renderGroupedBar(self, data: ChartData, outputPath: str):
        """그룹 막대 — 다중 범주 비교"""
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=self.style['figsize'])
        self._applyBaseStyle(fig, ax)
        colors = self.style['colors']

        numSeries = len(data.series)
        x = np.arange(len(data.labels))
        width = 0.8 / numSeries

        for i, (seriesName, values) in enumerate(data.series.items()):
            offset = (i - numSeries / 2 + 0.5) * width
            bars = ax.bar(x + offset, values, width, label=seriesName,
                         color=colors[i % len(colors)])
            # 값 레이블
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        self._formatValue(val, data.unit),
                        ha='center', va='bottom',
                        fontsize=self.style['value_size'] - 1)

        ax.set_xticks(x)
        ax.set_xticklabels(data.labels, rotation=45 if len(data.labels) > 6 else 0,
                           ha='right', fontsize=self.style['label_size'])
        ax.set_title(data.title, fontsize=self.style['title_size'],
                     fontweight='bold', pad=15)
        ax.legend(fontsize=self.style['label_size'])
        plt.tight_layout()
        fig.savefig(outputPath, dpi=self.style['dpi'],
                    facecolor=fig.get_facecolor(), bbox_inches='tight')
        plt.close(fig)

    def renderPie(self, data: ChartData, outputPath: str):
        """파이/도넛 차트 — 구성 비율"""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=self.style['figsize'])
        fig.set_facecolor(self.style['background'])
        ax.set_facecolor(self.style['background'])
        colors = self.style['colors']

        seriesName = list(data.series.keys())[0]
        values = data.series[seriesName]
        sliceColors = [colors[i % len(colors)] for i in range(len(values))]

        # 도넛 스타일 (가운데 구멍)
        wedges, texts, autotexts = ax.pie(
            values, labels=data.labels, colors=sliceColors,
            autopct='%1.1f%%', startangle=90, pctdistance=0.8,
            wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2))

        # 텍스트 스타일
        for text in texts:
            text.set_fontsize(self.style['label_size'])
        for autotext in autotexts:
            autotext.set_fontsize(self.style['value_size'])
            autotext.set_fontweight('bold')

        # dark 모드 텍스트 색상
        if self.style['background'] != '#FFFFFF':
            for text in texts:
                text.set_color('#CCCCCC')

        ax.set_title(data.title, fontsize=self.style['title_size'],
                     fontweight='bold', pad=20,
                     color='#EEEEEE' if self.style['background'] != '#FFFFFF' else '#333333')
        plt.tight_layout()
        fig.savefig(outputPath, dpi=self.style['dpi'],
                    facecolor=fig.get_facecolor(), bbox_inches='tight')
        plt.close(fig)

    def renderHeatmap(self, data: ChartData, outputPath: str):
        """히트맵 — 매트릭스 시각화"""
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=self.style['figsize'])
        self._applyBaseStyle(fig, ax)

        # series를 2D 배열로 변환
        seriesNames = list(data.series.keys())
        matrixData = np.array([data.series[s] for s in seriesNames])

        cmap = 'YlOrRd' if self.style['background'] == '#FFFFFF' else 'viridis'
        im = ax.imshow(matrixData, cmap=cmap, aspect='auto')

        # 축 레이블
        ax.set_xticks(np.arange(len(data.labels)))
        ax.set_xticklabels(data.labels, rotation=45, ha='right',
                          fontsize=self.style['label_size'])
        ax.set_yticks(np.arange(len(seriesNames)))
        ax.set_yticklabels(seriesNames, fontsize=self.style['label_size'])

        # 셀 값 표시
        for i in range(len(seriesNames)):
            for j in range(len(data.labels)):
                val = matrixData[i, j]
                ax.text(j, i, self._formatValue(val, data.unit),
                       ha='center', va='center',
                       fontsize=self.style['value_size'],
                       color='white' if val > matrixData.max() * 0.6 else 'black')

        fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_title(data.title, fontsize=self.style['title_size'],
                     fontweight='bold', pad=15)
        plt.tight_layout()
        fig.savefig(outputPath, dpi=self.style['dpi'],
                    facecolor=fig.get_facecolor(), bbox_inches='tight')
        plt.close(fig)

    def renderWaterfall(self, data: ChartData, outputPath: str):
        """워터폴 차트 — 분해 구조"""
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=self.style['figsize'])
        self._applyBaseStyle(fig, ax)

        seriesName = list(data.series.keys())[0]
        values = data.series[seriesName]
        n = len(values)

        # 누적 합계 계산
        cumulative = [0] * (n + 1)
        for i in range(n):
            cumulative[i + 1] = cumulative[i] + values[i]

        colors = []
        for v in values:
            if v >= 0:
                colors.append(self.style['colors'][0])  # 증가 색
            else:
                colors.append(self.style['colors'][3])  # 감소 색

        x = np.arange(n)
        bottoms = [min(cumulative[i], cumulative[i + 1]) for i in range(n)]
        heights = [abs(v) for v in values]

        bars = ax.bar(x, heights, bottom=bottoms, color=colors, width=0.6,
                      edgecolor='white', linewidth=1)

        # 연결선
        for i in range(n - 1):
            ax.plot([i + 0.3, i + 0.7], [cumulative[i + 1], cumulative[i + 1]],
                   color='gray', linewidth=0.8, linestyle='--')

        # 값 레이블
        for bar, val, bottom in zip(bars, values, bottoms):
            yPos = bottom + abs(val) / 2
            prefix = '+' if val > 0 else ''
            ax.text(bar.get_x() + bar.get_width() / 2, yPos,
                    f"{prefix}{self._formatValue(val, data.unit)}",
                    ha='center', va='center',
                    fontsize=self.style['value_size'], fontweight='bold',
                    color='white')

        ax.set_xticks(x)
        ax.set_xticklabels(data.labels, rotation=45, ha='right',
                          fontsize=self.style['label_size'])
        ax.set_title(data.title, fontsize=self.style['title_size'],
                     fontweight='bold', pad=15)
        plt.tight_layout()
        fig.savefig(outputPath, dpi=self.style['dpi'],
                    facecolor=fig.get_facecolor(), bbox_inches='tight')
        plt.close(fig)

    def renderScenarioBar(self, data: ChartData, outputPath: str):
        """시나리오 비교 차트 — BASE/UPSIDE/DOWNSIDE"""
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=self.style['figsize'])
        self._applyBaseStyle(fig, ax)

        seriesName = list(data.series.keys())[0]
        values = data.series[seriesName]

        # 시나리오별 색상 매핑
        scenarioColors = {
            'BASE': self.style['colors'][0],
            'UPSIDE': self.style['colors'][1],
            'BULL': self.style['colors'][1],
            'DOWNSIDE': self.style['colors'][3],
            'BEAR': self.style['colors'][3],
        }
        barColors = [scenarioColors.get(l.upper(), self.style['colors'][4])
                     for l in data.labels]

        x = np.arange(len(data.labels))
        bars = ax.bar(x, values, color=barColors, width=0.5,
                      edgecolor='white', linewidth=1)

        # 값 레이블
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.02,
                    self._formatValue(val, data.unit),
                    ha='center', va='bottom',
                    fontsize=self.style['value_size'] + 1, fontweight='bold')

        ax.set_xticks(x)
        ax.set_xticklabels(data.labels, fontsize=self.style['label_size'] + 1)
        ax.set_title(data.title, fontsize=self.style['title_size'],
                     fontweight='bold', pad=15)
        if data.unit:
            ax.set_ylabel(data.unit, fontsize=self.style['label_size'])
        plt.tight_layout()
        fig.savefig(outputPath, dpi=self.style['dpi'],
                    facecolor=fig.get_facecolor(), bbox_inches='tight')
        plt.close(fig)

    def _formatValue(self, val: float, unit: str = '') -> str:
        """숫자를 읽기 좋은 형식으로 변환"""
        if val is None:
            return ''
        absVal = abs(val)
        if absVal >= 1e12:
            formatted = f"{val / 1e12:.1f}T"
        elif absVal >= 1e9:
            formatted = f"{val / 1e9:.1f}B"
        elif absVal >= 1e6:
            formatted = f"{val / 1e6:.1f}M"
        elif absVal >= 1e3:
            formatted = f"{val / 1e3:.1f}K"
        elif absVal == int(absVal):
            formatted = f"{int(val)}"
        else:
            formatted = f"{val:.1f}"

        if unit and unit.startswith('$'):
            return f"${formatted}"
        elif unit:
            return f"{formatted}{unit}"
        return formatted


# ============================================================
# 차트 관리자
# ============================================================

class ChartManager:
    """차트 생성 관리 + 메타데이터"""

    def __init__(self, projectPath: str, styleName: str = 'consulting'):
        self.projectPath = Path(projectPath)
        self.extractor = ChartDataExtractor(projectPath)
        self.selector = ChartTypeSelector()
        self.renderer = ChartRenderer(styleName)

    def generateAll(self, division: Optional[str] = None,
                    factsOnly: bool = False,
                    outputDir: Optional[str] = None) -> list:
        """프로젝트 전체 차트 일괄 생성"""
        # 출력 디렉토리 설정
        if outputDir:
            chartsDir = Path(outputDir)
        else:
            chartsDir = self.projectPath / "reports" / "charts"
        chartsDir.mkdir(parents=True, exist_ok=True)

        print(f"=== 차트 자동 생성 시작 ===")
        print(f"프로젝트: {self.projectPath}")
        print(f"출력: {chartsDir}")
        if division:
            print(f"Division 필터: {division}")
        if factsOnly:
            print(f"모드: golden-facts 전용")
        print()

        # 1. 데이터 추출
        print("[1/4] 데이터 추출 중...")
        chartDataList = self.extractor.extractAll(division=division, factsOnly=factsOnly)
        print(f"  → 차트 후보 {len(chartDataList)}개 발견")

        if not chartDataList:
            print("\n차트 데이터가 없습니다. 다음을 확인하세요:")
            print("  - findings/golden-facts.yaml 파일이 존재하는지")
            print("  - findings/*/division-synthesis.yaml 파일이 존재하는지")
            print("  - reports/report-docs.md에 마크다운 테이블이 있는지")
            return []

        # 2. 차트 유형 선택
        print("[2/4] 차트 유형 선택 중...")
        for cd in chartDataList:
            cd.chart_type = self.selector.select(cd)
        typeCounts = {}
        for cd in chartDataList:
            typeCounts[cd.chart_type] = typeCounts.get(cd.chart_type, 0) + 1
        for t, c in typeCounts.items():
            print(f"  → {t}: {c}개")

        # 3. 렌더링
        print("[3/4] 차트 렌더링 중...")
        chartMetas = []
        for idx, cd in enumerate(chartDataList, 1):
            chartId = f"CHT-{idx:03d}"
            # 파일명 생성 (안전한 문자만)
            safeTitle = re.sub(r'[^\w가-힣\s-]', '', cd.title)[:40].strip()
            safeTitle = re.sub(r'\s+', '-', safeTitle)
            fileName = f"{chartId}-{safeTitle}.png"
            outputPath = chartsDir / fileName

            try:
                self.renderer.render(cd, str(outputPath))
                meta = ChartMeta(
                    chart_id=chartId,
                    chart_type=cd.chart_type,
                    title=cd.title,
                    data_source=os.path.relpath(cd.source_file, self.projectPath),
                    related_claims=cd.related_claims,
                    file_path=str(outputPath.relative_to(self.projectPath)),
                )
                chartMetas.append(meta)
                print(f"  [{chartId}] {cd.chart_type:12s} → {fileName}")
            except Exception as e:
                print(f"  [{chartId}] 렌더링 실패 — {cd.title}: {e}")

        # 4. 인덱스 파일 생성
        print("[4/4] 차트 인덱스 생성 중...")
        indexPath = chartsDir.parent / "chart-index.yaml"
        self.saveChartIndex(chartMetas, str(indexPath))
        print(f"  → {indexPath}")

        print()
        print(f"=== 차트 생성 완료 ===")
        print(f"  {len(chartMetas)}개 차트 → {chartsDir}")
        print(f"  인덱스: {indexPath}")
        return chartMetas

    def saveChartIndex(self, charts: list, outputPath: str):
        """차트 인덱스 파일 생성 (PPT 연동용)"""
        import yaml

        indexData = {
            'charts': []
        }

        for meta in charts:
            entry = {
                'id': meta.chart_id,
                'type': meta.chart_type,
                'title': meta.title,
                'data_source': meta.data_source,
                'related_claims': meta.related_claims,
                'file': meta.file_path,
            }
            indexData['charts'].append(entry)

        with open(outputPath, 'w', encoding='utf-8') as f:
            yaml.dump(indexData, f, default_flow_style=False,
                     allow_unicode=True, sort_keys=False)


# ============================================================
# CLI 엔트리포인트
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="리서치 차트 자동 생성 — division-synthesis, golden-facts, report-docs에서 수치 데이터를 추출하여 PNG 차트로 렌더링")
    parser.add_argument("project", help="프로젝트 디렉토리명 (예: my-research)")
    parser.add_argument("--division", help="특정 Division만 처리 (예: market, finance)")
    parser.add_argument("--facts-only", action="store_true",
                        help="golden-facts.yaml만으로 차트 생성")
    parser.add_argument("--style", default="consulting",
                        choices=["consulting", "minimal", "dark"],
                        help="차트 스타일 (기본: consulting)")
    parser.add_argument("--output-dir",
                        help="차트 출력 디렉토리 (기본: {project}/reports/charts/)")

    args = parser.parse_args()

    # 의존성 확인
    if not checkDependencies():
        sys.exit(1)

    # 프로젝트 경로 확인
    repoDir = Path(__file__).resolve().parent.parent
    projectPath = repoDir / args.project

    if not projectPath.exists():
        print(f"프로젝트 디렉토리가 없습니다: {projectPath}")
        sys.exit(1)

    # 차트 생성
    manager = ChartManager(str(projectPath), styleName=args.style)
    charts = manager.generateAll(
        division=args.division,
        factsOnly=args.facts_only,
        outputDir=args.output_dir,
    )

    if charts:
        print(f"\n열기: open {projectPath / 'reports' / 'charts'}")


if __name__ == "__main__":
    main()
