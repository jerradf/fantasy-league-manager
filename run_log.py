import subprocess
from datetime import datetime
from pathlib import Path


def write_run_log(lines, base_dir="logs/2026/sleeper"):
    base = Path(base_dir)
    if not base.is_absolute():
        base = Path(__file__).resolve().parent / base
    base.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    path = base / (now.strftime("%Y-%m-%d_%H%M") + ".md")
    body = "# Run log\n" + now.isoformat(timespec="seconds") + "\n\n" + "\n".join(str(x) for x in lines) + "\n"
    path.write_text(body, encoding="utf-8")
    return path


def commit_and_push_log(path):
    root = Path(__file__).resolve().parent
    try:
        rel = Path(path).resolve().relative_to(root)
    except Exception:
        rel = Path(path)
    for cmd in (["git", "add", str(rel)], ["git", "commit", "-m", "Add run log"], ["git", "push"]):
        try:
            result = subprocess.run(cmd, cwd=str(root), check=False, capture_output=True, text=True)
            if result.returncode != 0:
                print("git step failed:", " ".join(cmd), result.stderr.strip())
        except Exception as exc:
            print("git step error:", " ".join(cmd), exc)
