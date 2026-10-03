"""
data フォルダの CSV を GitHub にプッシュするモジュール。
status.json は Contents API で別途更新されるため CSV のみを対象とする。
認証は raspi/config/config.json の github_token を使用する。
"""

import glob
import json
import os
import subprocess

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config/config.json")
_REPO_ROOT   = os.path.join(os.path.dirname(__file__), "../../")


def _load_token() -> str | None:
    try:
        with open(_CONFIG_PATH) as f:
            return json.load(f).get("github_token")
    except Exception:
        return None


def _run(cmd: list[str], cwd: str) -> tuple[bool, str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout + result.stderr


def git_push_data() -> bool:
    """
    data/*.csv の変更をステージ・コミット・プッシュする。

    Returns:
        成功時 True、変更なし・失敗時 False
    """
    repo  = os.path.abspath(_REPO_ROOT)
    token = _load_token()

    # リモートURLにトークンを埋め込む（一時的に上書き）
    original_url = None
    if token:
        ok, out = _run(["git", "remote", "get-url", "origin"], repo)
        if not ok:
            print(f"[git_push] remote取得失敗: {out}")
            return False
        original_url = out.strip()
        if "github.com" in original_url and "@" not in original_url:
            auth_url = original_url.replace("https://", f"https://{token}@")
            _run(["git", "remote", "set-url", "origin", auth_url], repo)

    try:
        # リモートの変更（status.json 等）を先に取り込む
        _run(["git", "pull", "--rebase"], repo)

        # data/*.csv のみステージ
        csv_files = glob.glob(os.path.join(repo, "data", "*.csv"))
        if not csv_files:
            print("[git_push] CSVファイルなし、スキップ")
            return False

        ok, out = _run(["git", "add"] + csv_files, repo)
        if not ok:
            print(f"[git_push] git add 失敗: {out}")
            return False

        # 差分があるか確認
        ok, _ = _run(["git", "diff", "--cached", "--quiet"], repo)
        if ok:
            print("[git_push] CSVに変更なし、スキップ")
            return False

        ok, out = _run(["git", "commit", "-m", "data: auto push csv"], repo)
        if not ok:
            print(f"[git_push] git commit 失敗: {out}")
            return False

        ok, out = _run(["git", "push"], repo)
        if not ok:
            print(f"[git_push] git push 失敗: {out}")
            return False

        print("[git_push] CSVプッシュ完了")
        return True

    finally:
        if original_url:
            _run(["git", "remote", "set-url", "origin", original_url], repo)
