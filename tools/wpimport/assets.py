"""画像・添付ファイルのダウンロードとキャッシュを担当するモジュール。"""

from __future__ import annotations

from pathlib import Path

import requests


class AssetManager:
    """URL からファイルを取得し、ローカルに保存する。

    同じ URL は 1 度だけダウンロードし、以降はメモリ上のキャッシュを再利用する。
    ダウンロードに失敗した URL は `failed` に記録され、処理は継続される。
    """

    def __init__(self, download: bool = True, timeout: int = 15, session: requests.Session | None = None):
        self.download = download
        self.timeout = timeout
        self.session = session or requests.Session()
        self._cache: dict[str, bytes | None] = {}
        self.failed: list[tuple[str, str]] = []
        self.saved: set[str] = set()

    def _fetch(self, url: str) -> bytes | None:
        if url in self._cache:
            return self._cache[url]
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.content
        except requests.RequestException as exc:
            self.failed.append((url, str(exc)))
            data = None
        self._cache[url] = data
        return data

    def save(self, url: str, dest_path: Path) -> bool:
        """url の内容を dest_path に保存する。既に存在する場合は上書きしない。"""
        if not self.download:
            return False
        if dest_path.exists():
            self.saved.add(url)
            return True
        data = self._fetch(url)
        if data is None:
            return False
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(data)
        self.saved.add(url)
        return True
