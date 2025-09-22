"""
调度包装脚本：
- 正常任务：每天21:00调用 licence_management
- 补偿任务：每天10:30 检查上一日21:00是否成功执行；若未执行则补跑一次
- 日志：scheduled_runner.log 超过1MB时自动轮转归档
"""

from __future__ import annotations
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "logs"
STATE_FILE = STATE_DIR / "last_success_iso.txt"
LOG_FILE = STATE_DIR / "scheduled_runner.log"
MAX_LOG_BYTES = 1 * 1024 * 1024  # 1MB


def _rotate_log_if_needed() -> None:
    STATE_DIR.mkdir(exist_ok=True)
    if LOG_FILE.exists() and LOG_FILE.stat().st_size >= MAX_LOG_BYTES:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = STATE_DIR / f"scheduled_runner_{ts}.log"
        try:
            LOG_FILE.replace(backup)
        except Exception:
            # 失败则尝试复制并清空
            try:
                content = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
                backup.write_text(content, encoding="utf-8")
                LOG_FILE.write_text("", encoding="utf-8")
            except Exception:
                pass


def read_last_success_time() -> datetime | None:
    try:
        if not STATE_FILE.exists():
            return None
        text = STATE_FILE.read_text(encoding="utf-8").strip()
        if not text:
            return None
        return datetime.fromisoformat(text)
    except Exception:
        return None


def write_last_success_time(ts: datetime) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(ts.isoformat(), encoding="utf-8")


def run_licence_check() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "licence_management"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    _rotate_log_if_needed()
    with LOG_FILE.open("a", encoding="utf-8") as f:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{now}] returncode={result.returncode}\n")
        if result.stdout:
            f.write(result.stdout + "\n")
        if result.stderr:
            f.write(result.stderr + "\n")
    return result.returncode == 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    now = datetime.now()

    if mode == "run":
        ok = run_licence_check()
        if ok:
            write_last_success_time(now)
        sys.exit(0 if ok else 1)

    if mode == "catchup":
        last_ok = read_last_success_time()
        yesterday = (now - timedelta(days=1)).date()
        need_catchup = (last_ok is None) or (last_ok.date() < yesterday)
        if need_catchup:
            ok = run_licence_check()
            if ok:
                write_last_success_time(now)
            sys.exit(0 if ok else 1)
        else:
            sys.exit(0)

    print("Usage: python scripts/scheduled_runner.py [run|catchup]")
    sys.exit(2)


if __name__ == "__main__":
    main() 