"""WordPress の本文 (HTML) を、画像・リンクをローカル参照に置き換えたうえで Markdown に変換する。"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

from bs4 import BeautifulSoup, Comment
from markdownify import markdownify as html_to_markdown

from .assets import AssetManager
from .classify import KIND_BLOG, KIND_ERRORS, KIND_JOB

UPLOADS_MARKER = "/wp-content/uploads/"

# 記事本文と同じディレクトリに連番で配置する種別 (nnnn_mmm.ext)
LOCAL_NUMBERED_KINDS = {KIND_BLOG, KIND_JOB, KIND_ERRORS}

# WordPress のカテゴリアーカイブ (?cat=N) へのリンクを、Hugo で生成される目次ページの
# パスへ書き換える。term_id は WordPress.xml の <wp:category> で定義されているもの。
CATEGORY_ARCHIVE_URLS = {
    5: "/job/",  # 「しごと情報」 (nicename: offers)
    10: "/blog/",  # 「ブログ」 (nicename: blog)
}


def _is_upload_url(url: str) -> bool:
    return UPLOADS_MARKER in url


def _extract_referenced_post_id(url: str) -> int | None:
    """WordPress の旧パーマリンク (?p=N や ?page_id=N) が指す投稿 ID を取り出す。"""
    query = urlsplit(url).query
    if not query:
        return None
    qs = parse_qs(query)
    for key in ("p", "page_id"):
        if key in qs:
            try:
                return int(qs[key][0])
            except (TypeError, ValueError):
                return None
    return None


def _extract_category_id(url: str) -> int | None:
    """WordPress のカテゴリアーカイブリンク (?cat=N) が指すカテゴリ ID を取り出す。"""
    query = urlsplit(url).query
    if not query:
        return None
    qs = parse_qs(query)
    if "cat" in qs:
        try:
            return int(qs["cat"][0])
        except (TypeError, ValueError):
            return None
    return None


# 「しごと情報」(job) の記事にある 2 列テーブルで、見出し行が空のもの (`|  |  |`) を
# `| 項目 | 内容 |` に置き換えるための正規表現。
JOB_EMPTY_TABLE_HEADER_RE = re.compile(
    r"^\|\s*\|\s*\|\s*\n\|\s*:?-+:?\s*\|\s*:?-+:?\s*\|\s*$",
    re.MULTILINE,
)


def _fix_job_table_headers(markdown_text: str) -> str:
    return JOB_EMPTY_TABLE_HEADER_RE.sub(
        "| 項目 | 内容 |\n| --- | --- |", markdown_text
    )


def _is_internal_link(url: str, base_url: str) -> bool:
    if url.startswith("#"):
        return False
    if url.startswith("/"):
        return True
    base_netloc = urlsplit(base_url).netloc
    return urlsplit(url).netloc == base_netloc


class ContentProcessor:
    """WPItem 本文の HTML を Markdown へ変換するクラス。"""

    def __init__(
        self, base_url: str, asset_manager: AssetManager, url_map: dict[int, str]
    ):
        self.base_url = base_url
        self.asset_manager = asset_manager
        self.url_map = url_map

    def process(self, html: str, kind: str, post_id: int, image_dest_dir: Path) -> str:
        soup = BeautifulSoup(html or "", "html.parser")

        # Gutenberg のブロックコメント (<!-- wp:xxx --> など) を含む HTML コメントを除去
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        local_refs: dict[str, str] = {}
        counter = {"n": 0}

        def local_asset_ref(url: str) -> str:
            if url in local_refs:
                return local_refs[url]
            counter["n"] += 1
            basename = url.split("?", 1)[0].rsplit("/", 1)[-1]
            ext = basename.rsplit(".", 1)[-1].lower() if "." in basename else "jpg"
            if kind in LOCAL_NUMBERED_KINDS:
                filename = f"{post_id}_{counter['n']:03d}.{ext}"
                ref = filename
            else:
                filename = basename
                ref = f"/images/{filename}"
            absolute_url = urljoin(self.base_url, url)
            self.asset_manager.save(absolute_url, image_dest_dir / filename)
            local_refs[url] = ref
            return ref

        for img in soup.find_all("img"):
            src = img.get("src")
            if src and _is_upload_url(src):
                img["src"] = local_asset_ref(src)

        for anchor in soup.find_all("a"):
            href = anchor.get("href")
            if not href:
                continue
            if _is_upload_url(href):
                anchor["href"] = local_asset_ref(href)
            elif _is_internal_link(href, self.base_url):
                referenced_id = _extract_referenced_post_id(href)
                category_id = _extract_category_id(href)
                if referenced_id is not None and referenced_id in self.url_map:
                    anchor["href"] = self.url_map[referenced_id]
                elif category_id is not None and category_id in CATEGORY_ARCHIVE_URLS:
                    anchor["href"] = CATEGORY_ARCHIVE_URLS[category_id]

        cleaned_html = str(soup)
        markdown_text = html_to_markdown(
            cleaned_html,
            heading_style="ATX",
            bullets="-",
            strip=["script", "style"],
        )
        markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text.strip()) + "\n"

        if kind == KIND_JOB:
            markdown_text = _fix_job_table_headers(markdown_text)

        return markdown_text
