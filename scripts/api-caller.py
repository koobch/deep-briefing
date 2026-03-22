#!/usr/bin/env python3
"""
범용 API 호출 래퍼 — Leaf 에이전트가 데이터 수집 시 사용.
DART, Steam, FRED, ECOS 등 리서치 API를 통합 인터페이스로 제공한다.

사용법:
  python scripts/api-caller.py --api dart --action search_company --query "{기업명}" --output findings/market/dart-result.yaml
  python scripts/api-caller.py --api steam --action get_app_details --params '{"app_id": 730}' --output findings/product/steam-result.yaml
  python scripts/api-caller.py --api fred --action get_series --params '{"series_id": "GDP", "start_date": "2020-01-01", "end_date": "2025-12-31"}' --output findings/finance/fred-result.yaml
  python scripts/api-caller.py --api ecos --action get_stat_data --params '{"stat_code": "200Y001", "item_code": "10111", "start_date": "2020", "end_date": "2025"}' --output findings/finance/ecos-result.yaml
"""

import argparse
import json
import os
import sys
import time
import csv
import io
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv


# ============================================================
# 공통 베이스 클래스
# ============================================================

class APICallerBase:
    """모든 API 클라이언트의 공통 베이스 클래스"""

    # 서브클래스에서 오버라이드
    API_NAME = "base"
    ENV_KEY_NAME = None  # 환경변수 이름 (예: "DART_API_KEY")
    REQUIRES_KEY = True  # API 키 필수 여부

    def __init__(self):
        """환경변수에서 API 키를 로드한다."""
        self.api_key = None
        self.session = requests.Session()
        self._load_env()

    def _load_env(self):
        """프로젝트 루트의 .env 파일에서 환경변수 로드"""
        # 스크립트 위치 기준으로 프로젝트 루트 탐색
        scriptDir = Path(__file__).resolve().parent
        projectRoot = scriptDir.parent
        envPath = projectRoot / ".env"
        if envPath.exists():
            load_dotenv(envPath)

        if self.ENV_KEY_NAME:
            self.api_key = os.environ.get(self.ENV_KEY_NAME)

    def is_available(self) -> bool:
        """API 키가 설정되어 있는지 확인. 키 불필요 API는 항상 True."""
        if not self.REQUIRES_KEY:
            return True
        return bool(self.api_key) and self.api_key != f"your_{self.API_NAME}_api_key_here"

    # === API 쿼터 관리 ===
    QUOTA_FILE = None  # 프로젝트별 api-quota.yaml 경로 (호출 시 설정)

    @classmethod
    def _get_quota_path(cls):
        """프로젝트 디렉토리에서 api-quota.yaml 경로를 반환"""
        # 환경변수 또는 인자로 전달된 프로젝트 경로 사용
        # 1순위: 환경변수 PROJECT_DIR
        # 2순위: --output 경로에서 프로젝트 디렉토리 추론 (findings/ 상위)
        # 3순위: 현재 디렉토리에서 */data/api-quota.yaml 탐색
        project_dir = os.environ.get('PROJECT_DIR', '')
        if not project_dir:
            # 현재 디렉토리 하위에서 api-quota.yaml 탐색
            for entry in os.listdir('.'):
                candidate = os.path.join(entry, 'data', 'api-quota.yaml')
                if os.path.isdir(entry) and os.path.exists(candidate):
                    project_dir = entry
                    break
        if not project_dir:
            project_dir = '.'
        return os.path.join(project_dir, 'data', 'api-quota.yaml')

    @classmethod
    def check_quota(cls, api_name):
        """호출 전 쿼터 확인. 한도 도달 시 False 반환"""
        quota_path = cls._get_quota_path()
        if not os.path.exists(quota_path):
            return True  # 쿼터 파일 없으면 제한 없음

        with open(quota_path, 'r') as f:
            quotas = yaml.safe_load(f) or {}

        api_quota = quotas.get(api_name, {})
        daily_limit = api_quota.get('daily_limit', float('inf'))
        used_today = api_quota.get('used_today', 0)
        reset_at = api_quota.get('reset_at', '')

        # 날짜 변경 시 리셋
        if reset_at and datetime.now().strftime('%Y-%m-%d') > reset_at[:10]:
            api_quota['used_today'] = 0
            api_quota['reset_at'] = datetime.now().strftime('%Y-%m-%dT00:00:00')
            cls._save_quota(quota_path, quotas)
            return True

        if used_today >= daily_limit:
            print(f"⚠️  {api_name} 일일 쿼터 소진 ({used_today}/{daily_limit})")
            return False
        return True

    @classmethod
    def update_quota(cls, api_name, count=1):
        """호출 후 사용량 업데이트"""
        quota_path = cls._get_quota_path()
        if not os.path.exists(quota_path):
            return

        with open(quota_path, 'r') as f:
            quotas = yaml.safe_load(f) or {}

        if api_name not in quotas:
            return

        quotas[api_name]['used_today'] = quotas[api_name].get('used_today', 0) + count
        cls._save_quota(quota_path, quotas)

    @classmethod
    def _save_quota(cls, path, quotas):
        """쿼터 파일 저장"""
        with open(path, 'w') as f:
            yaml.dump(quotas, f, default_flow_style=False, allow_unicode=True)

    def call_with_retry(self, url: str, params: dict = None, headers: dict = None,
                        maxRetries: int = 3, timeout: int = 10, method: str = "GET") -> requests.Response:
        """
        재시도 로직이 포함된 HTTP 호출.
        지수 백오프: 1초 → 2초 → 4초.
        429 (Rate Limit) 시 10초 대기 후 재시도.
        """
        # 쿼터 확인
        if not self.check_quota(self.API_NAME):
            raise Exception(f"{self.API_NAME} 일일 쿼터 소진. PM에 에스컬레이션 필요.")

        lastException = None
        for attempt in range(maxRetries):
            try:
                if method.upper() == "GET":
                    resp = self.session.get(url, params=params, headers=headers, timeout=timeout)
                elif method.upper() == "POST":
                    resp = self.session.post(url, json=params, headers=headers, timeout=timeout)
                else:
                    raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")

                # Rate Limit 처리
                if resp.status_code == 429:
                    waitTime = 10
                    print(f"[{self.API_NAME}] Rate limit 도달. {waitTime}초 대기 후 재시도 ({attempt + 1}/{maxRetries})",
                          file=sys.stderr)
                    time.sleep(waitTime)
                    continue

                # 서버 에러 시 재시도
                if resp.status_code >= 500:
                    waitTime = 2 ** attempt
                    print(f"[{self.API_NAME}] 서버 에러 {resp.status_code}. {waitTime}초 후 재시도 ({attempt + 1}/{maxRetries})",
                          file=sys.stderr)
                    time.sleep(waitTime)
                    continue

                self.update_quota(self.API_NAME)
                return resp

            except requests.exceptions.Timeout:
                waitTime = 2 ** attempt
                print(f"[{self.API_NAME}] 타임아웃. {waitTime}초 후 재시도 ({attempt + 1}/{maxRetries})",
                      file=sys.stderr)
                lastException = TimeoutError(f"API 호출 타임아웃: {url}")
                time.sleep(waitTime)
            except requests.exceptions.ConnectionError as e:
                waitTime = 2 ** attempt
                print(f"[{self.API_NAME}] 연결 실패. {waitTime}초 후 재시도 ({attempt + 1}/{maxRetries})",
                      file=sys.stderr)
                lastException = e
                time.sleep(waitTime)

        # 모든 재시도 실패
        if lastException:
            raise lastException
        raise RuntimeError(f"[{self.API_NAME}] {maxRetries}회 재시도 후 실패: {url}")

    def validate_response(self, response: requests.Response) -> bool:
        """응답 유효성 기본 검증 (HTTP 상태 코드 기준)"""
        return 200 <= response.status_code < 300

    def save_result(self, data: dict, outputPath: str, fmt: str = "yaml"):
        """
        결과를 파일로 저장한다.
        output-format.md 호환 표준 포맷으로 래핑한다.
        """
        # 출력 디렉토리 생성
        outFile = Path(outputPath)
        outFile.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "yaml":
            with open(outFile, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        elif fmt == "json":
            with open(outFile, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        elif fmt == "csv":
            # data["data"]가 리스트인 경우 CSV로 변환
            rows = data.get("data", [])
            if not rows:
                print(f"[경고] CSV 저장할 데이터가 비어 있습니다.", file=sys.stderr)
                return
            if isinstance(rows, list) and len(rows) > 0 and isinstance(rows[0], dict):
                with open(outFile, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)
            else:
                # 단순 리스트인 경우
                with open(outFile, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    for row in rows:
                        writer.writerow([row] if not isinstance(row, (list, tuple)) else row)
        else:
            raise ValueError(f"지원하지 않는 출력 포맷: {fmt}")

        print(f"[{self.API_NAME}] 결과 저장 완료: {outFile}")

    def _wrap_result(self, action: str, query: str, data, status: str = "success") -> dict:
        """API 결과를 표준 포맷으로 래핑 (output-format.md 호환)"""
        return {
            "api_result": {
                "api": self.API_NAME,
                "action": action,
                "query": query,
                "called_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                "status": status,
                "data": data,
                "metadata": {
                    "type": "primary",
                    "reliability": "high",
                }
            }
        }


# ============================================================
# DART API 클라이언트 (한국 전자공시)
# ============================================================

class DARTClient(APICallerBase):
    """DART Open API 클라이언트 — 한국 기업 공시 데이터 조회"""

    API_NAME = "dart"
    ENV_KEY_NAME = "DART_API_KEY"
    BASE_URL = "https://opendart.fss.or.kr/api"

    # 기업 고유번호 캐시 (도메인 data-sources.md의 기업 조회표에서 로드 가능)
    # 아래는 빈 캐시. 캐시 미스 시 search_company API를 호출하여 동적 조회
    CORP_CODE_CACHE = {}

    def search_company(self, companyName: str) -> dict:
        """
        기업명으로 고유번호 검색.
        캐시에 있으면 캐시 사용, 없으면 API 호출.
        """
        # 캐시 조회
        if companyName in self.CORP_CODE_CACHE:
            corpCode = self.CORP_CODE_CACHE[companyName]
            return self._wrap_result("search_company", companyName, {
                "corp_code": corpCode,
                "corp_name": companyName,
                "source": "cache"
            })

        # API로 기업 검색 (고유번호 전체 목록에서 검색)
        # DART는 기업명 직접 검색 API가 없으므로, 공시 목록에서 검색
        url = f"{self.BASE_URL}/list.json"
        params = {
            "crtfc_key": self.api_key,
            "corp_name": companyName,
            "page_count": 10,
        }
        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("search_company", companyName, {
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}"
            }, status="error")

        data = resp.json()
        if data.get("status") != "000":
            return self._wrap_result("search_company", companyName, {
                "error": f"DART API 오류: {data.get('message', '알 수 없는 오류')}"
            }, status="error")

        # 검색 결과에서 고유번호 추출
        results = []
        for item in data.get("list", []):
            results.append({
                "corp_code": item.get("corp_code"),
                "corp_name": item.get("corp_name"),
                "stock_code": item.get("stock_code", ""),
                "report_nm": item.get("report_nm", ""),
            })

        return self._wrap_result("search_company", companyName, {
            "results": results,
            "source": "api"
        })

    def get_financials(self, corpCode: str, year: str, reportCode: str = "11011",
                       fsDiv: str = "CFS") -> dict:
        """
        재무제표 조회.
        reportCode: 11011=사업보고서, 11012=반기, 11013=1분기, 11014=3분기
        fsDiv: OFS=별도, CFS=연결
        """
        url = f"{self.BASE_URL}/fnlttSinglAcntAll.json"
        params = {
            "crtfc_key": self.api_key,
            "corp_code": corpCode,
            "bsns_year": year,
            "reprt_code": reportCode,
            "fs_div": fsDiv,
        }
        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("get_financials", corpCode, {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        if data.get("status") != "000":
            return self._wrap_result("get_financials", corpCode, {
                "error": f"DART API: {data.get('message', '알 수 없는 오류')}",
                "status_code": data.get("status")
            }, status="error")

        # 핵심 재무 항목 추출
        rawList = data.get("list", [])
        financials = []
        for item in rawList:
            financials.append({
                "account_nm": item.get("account_nm"),
                "thstrm_amount": item.get("thstrm_amount"),       # 당기
                "frmtrm_amount": item.get("frmtrm_amount"),       # 전기
                "bfefrmtrm_amount": item.get("bfefrmtrm_amount"), # 전전기
                "sj_nm": item.get("sj_nm"),                       # 재무제표 구분
            })

        return self._wrap_result("get_financials", f"{corpCode}/{year}/{fsDiv}", {
            "corp_code": corpCode,
            "bsns_year": year,
            "reprt_code": reportCode,
            "fs_div": fsDiv,
            "financials": financials,
            "total_items": len(financials),
        })

    def get_disclosure_list(self, corpCode: str, beginDate: str, endDate: str,
                            pblntfTy: str = "") -> dict:
        """
        공시 목록 조회.
        pblntfTy: A=정기공시, B=주요사항, C=발행공시, D=지분공시, E=기타공시
        """
        url = f"{self.BASE_URL}/list.json"
        params = {
            "crtfc_key": self.api_key,
            "corp_code": corpCode,
            "bgn_de": beginDate.replace("-", ""),
            "end_de": endDate.replace("-", ""),
            "page_count": 100,
        }
        if pblntfTy:
            params["pblntf_ty"] = pblntfTy

        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("get_disclosure_list", corpCode, {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        if data.get("status") != "000":
            return self._wrap_result("get_disclosure_list", corpCode, {
                "error": f"DART API: {data.get('message', '알 수 없는 오류')}"
            }, status="error")

        disclosures = []
        for item in data.get("list", []):
            disclosures.append({
                "rcept_no": item.get("rcept_no"),
                "rcept_dt": item.get("rcept_dt"),
                "report_nm": item.get("report_nm"),
                "flr_nm": item.get("flr_nm"),
                "pblntf_ty": item.get("pblntf_ty"),
            })

        return self._wrap_result("get_disclosure_list", f"{corpCode}/{beginDate}~{endDate}", {
            "corp_code": corpCode,
            "period": f"{beginDate} ~ {endDate}",
            "disclosures": disclosures,
            "total_count": len(disclosures),
        })

    def get_employees(self, corpCode: str, year: str, reportCode: str = "11011") -> dict:
        """직원 현황 조회"""
        url = f"{self.BASE_URL}/empSttus.json"
        params = {
            "crtfc_key": self.api_key,
            "corp_code": corpCode,
            "bsns_year": year,
            "reprt_code": reportCode,
        }
        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("get_employees", corpCode, {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        if data.get("status") != "000":
            return self._wrap_result("get_employees", corpCode, {
                "error": f"DART API: {data.get('message', '알 수 없는 오류')}"
            }, status="error")

        employees = []
        for item in data.get("list", []):
            employees.append({
                "fo_bbm": item.get("fo_bbm"),           # 사업부문
                "sexdstn": item.get("sexdstn"),         # 성별
                "rgllbr_co": item.get("rgllbr_co"),     # 정규직 수
                "cnttk_co": item.get("cnttk_co"),       # 계약직 수
                "sm": item.get("sm"),                   # 합계
                "avrg_cnwk_sdytrn": item.get("avrg_cnwk_sdytrn"),  # 평균근속연수
                "jan_salary_am": item.get("jan_salary_am"),          # 연간급여총액
            })

        return self._wrap_result("get_employees", f"{corpCode}/{year}", {
            "corp_code": corpCode,
            "bsns_year": year,
            "employees": employees,
        })

    # 액션 디스패치 맵
    def dispatch(self, action: str, query: str = "", params: dict = None) -> dict:
        """액션 이름으로 적절한 메서드를 호출한다."""
        params = params or {}
        actionMap = {
            "search_company": lambda: self.search_company(query),
            "get_financials": lambda: self.get_financials(
                corpCode=params.get("corp_code", self.CORP_CODE_CACHE.get(query, query)),
                year=params.get("year", str(datetime.now().year - 1)),
                reportCode=params.get("report_code", "11011"),
                fsDiv=params.get("fs_div", "CFS"),
            ),
            "get_disclosure_list": lambda: self.get_disclosure_list(
                corpCode=params.get("corp_code", self.CORP_CODE_CACHE.get(query, query)),
                beginDate=params.get("begin_date", f"{datetime.now().year - 1}-01-01"),
                endDate=params.get("end_date", datetime.now().strftime("%Y-%m-%d")),
                pblntfTy=params.get("pblntf_ty", ""),
            ),
            "get_employees": lambda: self.get_employees(
                corpCode=params.get("corp_code", self.CORP_CODE_CACHE.get(query, query)),
                year=params.get("year", str(datetime.now().year - 1)),
                reportCode=params.get("report_code", "11011"),
            ),
        }
        if action not in actionMap:
            return self._wrap_result(action, query, {
                "error": f"지원하지 않는 액션: {action}",
                "available_actions": list(actionMap.keys())
            }, status="error")
        return actionMap[action]()


# ============================================================
# Steam API 클라이언트 (PC 게임 데이터)
# ============================================================

class SteamClient(APICallerBase):
    """Steam Web API + Store API 클라이언트"""

    API_NAME = "steam"
    ENV_KEY_NAME = "STEAM_API_KEY"
    STORE_URL = "https://store.steampowered.com/api"
    API_URL = "https://api.steampowered.com"

    def get_app_details(self, appId: int) -> dict:
        """게임 상세 정보 조회 (Store API — 키 불필요)"""
        url = f"{self.STORE_URL}/appdetails"
        params = {"appids": str(appId), "l": "korean"}
        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("get_app_details", str(appId), {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        appData = data.get(str(appId), {})
        if not appData.get("success"):
            return self._wrap_result("get_app_details", str(appId), {
                "error": "앱 정보를 찾을 수 없습니다."
            }, status="error")

        info = appData.get("data", {})
        return self._wrap_result("get_app_details", str(appId), {
            "app_id": appId,
            "name": info.get("name"),
            "type": info.get("type"),
            "is_free": info.get("is_free"),
            "detailed_description": info.get("short_description", "")[:500],
            "developers": info.get("developers", []),
            "publishers": info.get("publishers", []),
            "price": info.get("price_overview", {}),
            "platforms": info.get("platforms", {}),
            "categories": [c.get("description") for c in info.get("categories", [])],
            "genres": [g.get("description") for g in info.get("genres", [])],
            "release_date": info.get("release_date", {}),
            "metacritic": info.get("metacritic", {}),
            "recommendations": info.get("recommendations", {}),
        })

    def get_player_count(self, appId: int) -> dict:
        """동시 접속자 수 조회 (API 키 필요)"""
        url = f"{self.API_URL}/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
        params = {"key": self.api_key, "appid": str(appId)}
        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("get_player_count", str(appId), {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        respData = data.get("response", {})
        return self._wrap_result("get_player_count", str(appId), {
            "app_id": appId,
            "player_count": respData.get("player_count", 0),
            "result": respData.get("result", 0),
        })

    def get_app_list(self) -> dict:
        """전체 앱 목록 조회 (키 불필요). 게임 검색에 사용."""
        url = f"{self.API_URL}/ISteamApps/GetAppList/v2/"
        resp = self.call_with_retry(url, timeout=30)
        if not self.validate_response(resp):
            return self._wrap_result("get_app_list", "", {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        apps = data.get("applist", {}).get("apps", [])
        return self._wrap_result("get_app_list", "", {
            "total_apps": len(apps),
            "note": "전체 목록은 대용량. --query로 필터링 권장.",
        })

    def search_app(self, gameName: str) -> dict:
        """게임명으로 앱 ID 검색 (Store 검색 API)"""
        url = "https://store.steampowered.com/api/storesearch/"
        params = {"term": gameName, "l": "korean", "cc": "KR"}
        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("search_app", gameName, {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "app_id": item.get("id"),
                "name": item.get("name"),
                "price": item.get("price", {}),
            })

        return self._wrap_result("search_app", gameName, {
            "query": gameName,
            "results": results,
            "total": len(results),
        })

    def get_reviews(self, appId: int, language: str = "all") -> dict:
        """게임 리뷰 요약 조회 (키 불필요)"""
        url = f"https://store.steampowered.com/appreviews/{appId}"
        params = {
            "json": 1,
            "language": language,
            "purchase_type": "all",
            "num_per_page": 0,  # 요약만
        }
        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("get_reviews", str(appId), {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        summary = data.get("query_summary", {})
        return self._wrap_result("get_reviews", str(appId), {
            "app_id": appId,
            "total_reviews": summary.get("total_reviews", 0),
            "total_positive": summary.get("total_positive", 0),
            "total_negative": summary.get("total_negative", 0),
            "review_score": summary.get("review_score", 0),
            "review_score_desc": summary.get("review_score_desc", ""),
        })

    def dispatch(self, action: str, query: str = "", params: dict = None) -> dict:
        params = params or {}
        actionMap = {
            "get_app_details": lambda: self.get_app_details(
                appId=int(params.get("app_id", query))
            ),
            "get_player_count": lambda: self.get_player_count(
                appId=int(params.get("app_id", query))
            ),
            "search_app": lambda: self.search_app(query),
            "get_reviews": lambda: self.get_reviews(
                appId=int(params.get("app_id", query)),
                language=params.get("language", "all"),
            ),
            "get_app_list": lambda: self.get_app_list(),
        }
        if action not in actionMap:
            return self._wrap_result(action, query, {
                "error": f"지원하지 않는 액션: {action}",
                "available_actions": list(actionMap.keys())
            }, status="error")
        return actionMap[action]()


# ============================================================
# FRED API 클라이언트 (미국 경제지표)
# ============================================================

class FREDClient(APICallerBase):
    """FRED (Federal Reserve Economic Data) 클라이언트"""

    API_NAME = "fred"
    ENV_KEY_NAME = "FRED_API_KEY"
    BASE_URL = "https://api.stlouisfed.org/fred"

    # 자주 사용하는 시리즈 ID (data-sources.md 기반)
    COMMON_SERIES = {
        "GDP": "GDP",
        "CPI": "CPIAUCSL",
        "환율": "DEXKOUS",
        "USD/KRW": "DEXKOUS",
        "실업률": "UNRATE",
        "PCE": "PCE",
        "개인소비지출": "PCE",
    }

    def get_series(self, seriesId: str, startDate: str = "", endDate: str = "") -> dict:
        """
        경제지표 시계열 데이터 조회.
        seriesId: FRED 시리즈 ID (예: GDP, CPIAUCSL)
        """
        # 별칭 → 실제 시리즈 ID 변환
        actualId = self.COMMON_SERIES.get(seriesId, seriesId)

        url = f"{self.BASE_URL}/series/observations"
        params = {
            "series_id": actualId,
            "api_key": self.api_key,
            "file_type": "json",
        }
        if startDate:
            params["observation_start"] = startDate
        if endDate:
            params["observation_end"] = endDate

        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("get_series", actualId, {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        if "error_code" in data:
            return self._wrap_result("get_series", actualId, {
                "error": f"FRED API: {data.get('error_message', '알 수 없는 오류')}"
            }, status="error")

        observations = []
        for obs in data.get("observations", []):
            val = obs.get("value", ".")
            observations.append({
                "date": obs.get("date"),
                "value": float(val) if val != "." else None,
            })

        return self._wrap_result("get_series", actualId, {
            "series_id": actualId,
            "title": data.get("title", actualId),
            "start": startDate or "earliest",
            "end": endDate or "latest",
            "observations": observations,
            "count": len(observations),
        })

    def search_series(self, keyword: str) -> dict:
        """키워드로 시리즈 검색"""
        url = f"{self.BASE_URL}/series/search"
        params = {
            "search_text": keyword,
            "api_key": self.api_key,
            "file_type": "json",
            "limit": 20,
        }
        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("search_series", keyword, {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        results = []
        for s in data.get("seriess", []):
            results.append({
                "id": s.get("id"),
                "title": s.get("title"),
                "frequency": s.get("frequency"),
                "units": s.get("units"),
                "observation_start": s.get("observation_start"),
                "observation_end": s.get("observation_end"),
            })

        return self._wrap_result("search_series", keyword, {
            "keyword": keyword,
            "results": results,
            "total": len(results),
        })

    def get_series_info(self, seriesId: str) -> dict:
        """시리즈 메타데이터 조회"""
        actualId = self.COMMON_SERIES.get(seriesId, seriesId)
        url = f"{self.BASE_URL}/series"
        params = {
            "series_id": actualId,
            "api_key": self.api_key,
            "file_type": "json",
        }
        resp = self.call_with_retry(url, params=params)
        if not self.validate_response(resp):
            return self._wrap_result("get_series_info", actualId, {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        seriesArr = data.get("seriess", [])
        if not seriesArr:
            return self._wrap_result("get_series_info", actualId, {
                "error": "시리즈를 찾을 수 없습니다."
            }, status="error")

        s = seriesArr[0]
        return self._wrap_result("get_series_info", actualId, {
            "id": s.get("id"),
            "title": s.get("title"),
            "frequency": s.get("frequency"),
            "units": s.get("units"),
            "seasonal_adjustment": s.get("seasonal_adjustment"),
            "observation_start": s.get("observation_start"),
            "observation_end": s.get("observation_end"),
            "notes": s.get("notes", "")[:500],
        })

    def dispatch(self, action: str, query: str = "", params: dict = None) -> dict:
        params = params or {}
        actionMap = {
            "get_series": lambda: self.get_series(
                seriesId=params.get("series_id", query),
                startDate=params.get("start_date", ""),
                endDate=params.get("end_date", ""),
            ),
            "search_series": lambda: self.search_series(query),
            "get_series_info": lambda: self.get_series_info(
                seriesId=params.get("series_id", query)
            ),
        }
        if action not in actionMap:
            return self._wrap_result(action, query, {
                "error": f"지원하지 않는 액션: {action}",
                "available_actions": list(actionMap.keys())
            }, status="error")
        return actionMap[action]()


# ============================================================
# ECOS API 클라이언트 (한국은행 경제통계)
# ============================================================

class ECOSClient(APICallerBase):
    """ECOS (한국은행 경제통계) 클라이언트"""

    API_NAME = "ecos"
    ENV_KEY_NAME = "ECOS_API_KEY"
    BASE_URL = "https://ecos.bok.or.kr/api"

    # 자주 사용하는 통계표 (data-sources.md 기반)
    COMMON_STATS = {
        "GDP": {"stat_code": "200Y001", "item_code": "10111", "cycle": "A"},
        "GDP성장률": {"stat_code": "200Y001", "item_code": "10111", "cycle": "A"},
        "CPI": {"stat_code": "901Y009", "item_code": "0", "cycle": "M"},
        "소비자물가": {"stat_code": "901Y009", "item_code": "0", "cycle": "M"},
        "환율": {"stat_code": "731Y001", "item_code": "0000001", "cycle": "D"},
        "원달러": {"stat_code": "731Y001", "item_code": "0000001", "cycle": "D"},
    }

    def get_stat_data(self, statCode: str, itemCode: str, startDate: str,
                      endDate: str, cycle: str = "A") -> dict:
        """
        통계 데이터 조회.
        cycle: A=연간, Q=분기, M=월간, D=일간
        ECOS URL 형식: /StatisticSearch/{key}/json/kr/{start}/{end}/{stat_code}/{cycle}/{startDate}/{endDate}/{itemCode}
        """
        url = (f"{self.BASE_URL}/StatisticSearch/{self.api_key}/json/kr"
               f"/1/100/{statCode}/{cycle}/{startDate}/{endDate}/{itemCode}")

        resp = self.call_with_retry(url)
        if not self.validate_response(resp):
            return self._wrap_result("get_stat_data", statCode, {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        statSearch = data.get("StatisticSearch", {})

        # 에러 처리
        if "list_total_count" not in statSearch:
            resultMsg = data.get("RESULT", {}).get("MESSAGE", "알 수 없는 오류")
            return self._wrap_result("get_stat_data", statCode, {
                "error": f"ECOS API: {resultMsg}"
            }, status="error")

        rows = statSearch.get("row", [])
        observations = []
        for row in rows:
            observations.append({
                "date": row.get("TIME"),
                "value": row.get("DATA_VALUE"),
                "stat_name": row.get("STAT_NAME"),
                "item_name": row.get("ITEM_NAME1"),
                "unit": row.get("UNIT_NAME"),
            })

        return self._wrap_result("get_stat_data", statCode, {
            "stat_code": statCode,
            "item_code": itemCode,
            "cycle": cycle,
            "period": f"{startDate} ~ {endDate}",
            "observations": observations,
            "count": len(observations),
        })

    def search_stat(self, keyword: str) -> dict:
        """통계표 검색"""
        url = (f"{self.BASE_URL}/StatisticTableList/{self.api_key}/json/kr"
               f"/1/20/{keyword}")

        resp = self.call_with_retry(url)
        if not self.validate_response(resp):
            return self._wrap_result("search_stat", keyword, {
                "error": f"HTTP {resp.status_code}"
            }, status="error")

        data = resp.json()
        tableList = data.get("StatisticTableList", {})
        rows = tableList.get("row", [])

        results = []
        for row in rows:
            results.append({
                "stat_code": row.get("STAT_CODE"),
                "stat_name": row.get("STAT_NAME"),
                "cycle": row.get("CYCLE"),
                "org_name": row.get("ORG_NAME"),
            })

        return self._wrap_result("search_stat", keyword, {
            "keyword": keyword,
            "results": results,
            "total": len(results),
        })

    def dispatch(self, action: str, query: str = "", params: dict = None) -> dict:
        params = params or {}

        # 별칭으로 간편 조회
        if action == "get_stat_data" and query in self.COMMON_STATS:
            preset = self.COMMON_STATS[query]
            params.setdefault("stat_code", preset["stat_code"])
            params.setdefault("item_code", preset["item_code"])
            params.setdefault("cycle", preset["cycle"])

        actionMap = {
            "get_stat_data": lambda: self.get_stat_data(
                statCode=params.get("stat_code", ""),
                itemCode=params.get("item_code", "0"),
                startDate=params.get("start_date", f"{datetime.now().year - 5}"),
                endDate=params.get("end_date", str(datetime.now().year)),
                cycle=params.get("cycle", "A"),
            ),
            "search_stat": lambda: self.search_stat(query),
        }
        if action not in actionMap:
            return self._wrap_result(action, query, {
                "error": f"지원하지 않는 액션: {action}",
                "available_actions": list(actionMap.keys())
            }, status="error")
        return actionMap[action]()


# ============================================================
# 클라이언트 레지스트리
# ============================================================

CLIENT_REGISTRY = {
    "dart": DARTClient,
    "steam": SteamClient,
    "fred": FREDClient,
    "ecos": ECOSClient,
}


# ============================================================
# CLI 인터페이스
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="리서치 API 자동 호출 래퍼 — Leaf 에이전트용",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # DART — 기업 재무제표 조회
  python scripts/api-caller.py --api dart --action get_financials --query "기업명" --output findings/dart.yaml

  # DART — 기업 직원 현황
  python scripts/api-caller.py --api dart --action get_employees --query "기업명" --output findings/dart-emp.yaml

  # Steam — 게임 검색
  python scripts/api-caller.py --api steam --action search_app --query "Counter-Strike" --output findings/steam.yaml

  # Steam — 게임 상세 (app_id 직접 지정)
  python scripts/api-caller.py --api steam --action get_app_details --params '{"app_id": 730}' --output findings/steam-detail.yaml

  # FRED — GDP 시계열
  python scripts/api-caller.py --api fred --action get_series --query "GDP" --params '{"start_date": "2020-01-01"}' --output findings/fred-gdp.yaml

  # ECOS — GDP 성장률 (별칭 사용)
  python scripts/api-caller.py --api ecos --action get_stat_data --query "GDP" --output findings/ecos-gdp.yaml

  # 지원 액션 확인 (존재하지 않는 액션 입력)
  python scripts/api-caller.py --api dart --action help --query "" --output /dev/null
        """)

    parser.add_argument("--api", required=True, choices=list(CLIENT_REGISTRY.keys()),
                        help="사용할 API (dart, steam, fred, ecos)")
    parser.add_argument("--action", required=True,
                        help="API 액션 (예: search_company, get_financials, get_series)")
    parser.add_argument("--query", default="",
                        help="검색 쿼리 또는 대상 (예: 기업명, 게임명, 시리즈 ID)")
    parser.add_argument("--params", default="{}",
                        help="추가 파라미터 (JSON 문자열, 예: '{\"year\": \"2024\"}')")
    parser.add_argument("--output", required=True,
                        help="출력 파일 경로 (예: findings/market/dart-result.yaml)")
    parser.add_argument("--format", default="yaml", choices=["yaml", "json", "csv"],
                        help="출력 포맷 (기본: yaml)")

    args = parser.parse_args()

    # JSON 파라미터 파싱
    try:
        extraParams = json.loads(args.params)
    except json.JSONDecodeError as e:
        print(f"[오류] --params JSON 파싱 실패: {e}", file=sys.stderr)
        sys.exit(1)

    # 클라이언트 생성
    clientClass = CLIENT_REGISTRY[args.api]
    client = clientClass()

    # API 키 확인
    if client.REQUIRES_KEY and not client.is_available():
        # 키 없음 → SKIP (에러가 아님)
        result = client._wrap_result(args.action, args.query, {
            "skip_reason": f"API 키 미설정 ({client.ENV_KEY_NAME}). .env 파일에 키를 추가하세요.",
            "key_issue_url": _get_key_url(args.api),
        }, status="skipped")
        client.save_result(result, args.output, args.format)
        print(f"[{args.api}] SKIP — API 키 미설정. 웹 검색으로 대체 필요.", file=sys.stderr)
        sys.exit(0)

    # API 호출
    try:
        result = client.dispatch(args.action, args.query, extraParams)
        client.save_result(result, args.output, args.format)

        # 결과 상태 출력
        status = result.get("api_result", {}).get("status", "unknown")
        if status == "success":
            print(f"[{args.api}] 성공 — {args.action} 완료. 저장: {args.output}")
        else:
            print(f"[{args.api}] {status} — {args.action}. 상세: {args.output}", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        # 예외 발생 시에도 에러 결과를 파일로 저장
        result = client._wrap_result(args.action, args.query, {
            "error": str(e),
            "error_type": type(e).__name__,
        }, status="error")
        client.save_result(result, args.output, args.format)
        print(f"[{args.api}] 오류 — {e}", file=sys.stderr)
        sys.exit(1)


def _get_key_url(apiName: str) -> str:
    """API 키 발급 URL 반환"""
    urls = {
        "dart": "https://opendart.fss.or.kr",
        "steam": "https://steamcommunity.com/dev/apikey",
        "fred": "https://fred.stlouisfed.org/docs/api/api_key.html",
        "ecos": "https://ecos.bok.or.kr/api/",
    }
    return urls.get(apiName, "")


if __name__ == "__main__":
    main()
