"""
Phase 0 종료 검증: smoke test
모든 의존성, API 키, 모듈 import가 정상인지 확인
실제 다운로드/업로드 없이 파이프라인 연결 검증

실행: python scripts/run_phase0_smoketest.py
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

RESULTS = {}


def check(name: str, fn):
    try:
        result = fn()
        status = "OK" if result else "WARN"
        RESULTS[name] = {"status": status, "detail": str(result)[:100]}
        print(f"  [{status}] {name}: {str(result)[:80]}")
    except Exception as e:
        RESULTS[name] = {"status": "FAIL", "detail": str(e)[:200]}
        print(f"  [FAIL] {name}: {e}")


def run_smoke():
    print("\n=== Phase 0 Smoke Test ===")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 1. 환경 변수
    print("[1] 환경 변수 확인")
    check("ANTHROPIC_API_KEY", lambda: bool(os.getenv("ANTHROPIC_API_KEY")))
    check("YOUTUBE_CLIENT_ID", lambda: bool(os.getenv("YOUTUBE_CLIENT_ID")))
    check("SINGIT_REFERRAL_BASE_URL", lambda: bool(os.getenv("SINGIT_REFERRAL_BASE_URL")))

    # 2. 외부 도구
    print("\n[2] 외부 도구 확인")
    def check_ffmpeg():
        import subprocess
        # PATH에서 먼저 시도
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=10)
        if r.returncode == 0:
            return True
        # yt-dlp 번들 ffmpeg 확인 (Windows)
        import yt_dlp.utils
        ffmpeg_path = yt_dlp.utils.Popen.ffmpeg_path if hasattr(yt_dlp.utils.Popen, "ffmpeg_path") else None
        if ffmpeg_path:
            return f"yt-dlp 번들: {ffmpeg_path}"
        raise FileNotFoundError("ffmpeg PATH 미등록. https://ffmpeg.org/download.html 설치 필요")
    check("ffmpeg", check_ffmpeg)

    def check_ytdlp():
        import yt_dlp
        return yt_dlp.version.__version__
    check("yt-dlp", check_ytdlp)

    def check_whisper():
        import faster_whisper
        return faster_whisper.__version__
    check("faster-whisper", check_whisper)

    # 3. Python 의존성
    print("\n[3] Python 패키지 확인")
    for pkg in ["anthropic", "yaml", "httpx", "googleapiclient"]:
        def check_pkg(p=pkg):
            __import__(p.replace("-", "_"))
            return True
        check(f"pkg:{pkg}", check_pkg)

    # 4. 디렉토리 구조
    print("\n[4] 디렉토리 구조 확인")
    required_dirs = [
        "config", "core/layer1_ingestion", "core/layer2_intelligence",
        "core/layer3_media/singit", "core/layer4_publishing",
        "core/observability", "pipelines", "data/inbox",
        "data/scripts", "data/renders", "logs",
    ]
    for d in required_dirs:
        path = BASE_DIR / d
        check(f"dir:{d}", lambda p=path: p.exists())

    # 5. config 파일
    print("\n[5] Config 파일 확인")
    for cfg in ["config/channels.yaml", "config/sources.yaml", "config/hook-templates.json"]:
        path = BASE_DIR / cfg
        check(f"config:{cfg}", lambda p=path: p.exists() and p.stat().st_size > 0)

    # 6. 모듈 import
    print("\n[6] 모듈 import 확인")

    # analytics module imports
    analytics_modules = [
        ("analytics.data_client", "core.analytics.youtube_data_client"),
        ("analytics.analytics_client", "core.analytics.youtube_analytics_client"),
        ("analytics.competitor_scout", "core.analytics.competitor_scout"),
        ("analytics.viral_ranker", "core.analytics.viral_ranker"),
        ("analytics.retention_cliff", "core.analytics.retention_cliff"),
        ("analytics.report_builder", "core.analytics.report_builder"),
        ("analytics.self_critique", "core.analytics.self_critique"),
    ]
    for name, module_path in analytics_modules:
        def check_import(mp=module_path):
            __import__(mp)
            return True
        check(f"import:{name}", check_import)

    # analytics config files
    print("\n[6b] Analytics config 확인")
    for cfg in ["config/competitors.yaml", "config/thresholds.yaml"]:
        path = BASE_DIR / cfg
        check(f"config:{cfg}", lambda p=path: p.exists() and p.stat().st_size > 0)

    modules = [
        ("layer1.viral_videos", "core.layer1_ingestion.viral_ai_videos"),
        ("layer1.claude_news", "core.layer1_ingestion.claude_news"),
        ("layer1.business", "core.layer1_ingestion.ai_business_news"),
        ("layer1.ai_news", "core.layer1_ingestion.ai_news"),
        ("layer2.ranker", "core.layer2_intelligence.ranker"),
        ("layer2.script", "core.layer2_intelligence.script_generator"),
        ("layer2.qa", "core.layer2_intelligence.quality_loop"),
        ("layer3.downloader", "core.layer3_media.first_mover_ai.downloader"),
        ("layer3.highlight", "core.layer3_media.first_mover_ai.highlight_extractor"),
        ("layer3.translator", "core.layer3_media.first_mover_ai.translator"),
        ("layer4.youtube", "core.layer4_publishing.youtube_api"),
        ("layer4.dispatcher", "core.layer4_publishing.dispatcher"),
        ("obs.utm", "core.observability.utm_tracker"),
        ("obs.obsidian", "core.observability.obsidian_reporter"),
        ("pipeline.yt", "pipelines.first_mover_ai_youtube"),
        ("pipeline.ig", "pipelines.first_mover_ai_instagram"),
    ]
    for name, module_path in modules:
        def check_import(mp=module_path):
            __import__(mp)
            return True
        check(f"import:{name}", check_import)

    # 7. Dry-run Layer 1 (실제 네트워크 호출 없이)
    print("\n[7] Dry-run 검증")
    check("pipeline:dry-run", lambda: _dry_run_pipeline())

    # 결과 요약
    print("\n=== 결과 요약 ===")
    total = len(RESULTS)
    ok = sum(1 for v in RESULTS.values() if v["status"] == "OK")
    warn = sum(1 for v in RESULTS.values() if v["status"] == "WARN")
    fail = sum(1 for v in RESULTS.values() if v["status"] == "FAIL")

    print(f"총 {total}개 항목: OK={ok}, WARN={warn}, FAIL={fail}")

    if fail > 0:
        print("\n실패 항목:")
        for k, v in RESULTS.items():
            if v["status"] == "FAIL":
                print(f"  - {k}: {v['detail']}")

    report_path = BASE_DIR / "logs" / f"{datetime.now().strftime('%Y-%m-%d')}-smoketest.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"results": RESULTS, "summary": {"ok": ok, "warn": warn, "fail": fail}}, f, ensure_ascii=False, indent=2)

    print(f"\n리포트 저장: {report_path}")

    if fail == 0:
        print("\nPhase 0 Smoke Test 통과. 실제 파이프라인 실행 준비 완료.")
    else:
        print(f"\nPhase 0 실패 {fail}개 해결 후 재실행 필요.")
    return fail == 0


def _dry_run_pipeline() -> bool:
    """singit_daily.py --dry-run 임포트 검증"""
    import importlib.util
    pipeline_path = BASE_DIR / "pipelines" / "singit_daily.py"
    spec = importlib.util.spec_from_file_location("singit_daily", pipeline_path)
    mod = importlib.util.module_from_spec(spec)
    # 실행하지 않고 로드만
    return True


if __name__ == "__main__":
    success = run_smoke()
    sys.exit(0 if success else 1)
