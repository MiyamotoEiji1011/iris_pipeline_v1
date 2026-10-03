"""
data フォルダの変更を GitHub にプッシュするモジュール。
認証は raspi/config/config.json の github_token を使用する。
"""

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
    data/ フォルダの変更をステージ・コミット・プッシュする。

    Returns:
        成功時 True、変更なし・失敗時 False
    """
    repo = os.path.abspath(_REPO_ROOT)
    token = _load_token()

    # リモートURLにトークンを埋め込む（一時的に上書き）
    if token:
        ok, out = _run(["git", "remote", "get-url", "origin"], repo)
        if not ok:
            print(f"[git_push] remote取得失敗: {out}")
            return False
        original_url = out.strip()

        # https://github.com/user/repo.git → https://<token>@github.com/user/repo.git
        if "github.com" in original_url and "@" not in original_url:
            auth_url = original_url.replace("https://", f"https://{token}@")
            _run(["git", "remote", "set-url", "origin", auth_url], repo)

    try:
        # data/ フォルダのみステージ
        ok, out = _run(["git", "add", "data/"], repo)
        if not ok:
            print(f"[git_push] git add 失敗: {out}")
            return False

        # 差分があるか確認
        ok, out = _run(["git", "diff", "--cached", "--quiet"], repo)
        if ok:
            print("[git_push] data/ に変更なし、スキップ")
            return False

        # コミット
        ok, out = _run(["git", "commit", "-m", "data: auto push"], repo)
        if not ok:
            print(f"[git_push] git commit 失敗: {out}")
            return False

        # プッシュ
        ok, out = _run(["git", "push"], repo)
        if not ok:
            print(f"[git_push] git push 失敗: {out}")
            return False

        print("[git_push] プッシュ完了")
        return True

    finally:
        # 認証URLを元に戻す
        if token and "original_url" in dir():
            _run(["git", "remote", "set-url", "origin", original_url], repo)
