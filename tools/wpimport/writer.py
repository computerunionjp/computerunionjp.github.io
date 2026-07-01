"""Hugo 用の front matter (メタ情報) を付与した Markdown ファイルの内容を組み立てる。"""

from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import unquote

import yaml

from .classify import KIND_BLOG, KIND_ERRORS, KIND_JOB
from .parser import WPItem

CATEGORY_LABELS = {
    KIND_BLOG: ["ブログ"],
    KIND_JOB: ["しごと情報"],
    KIND_ERRORS: ["ブログ", "しごと情報"],
}

ERROR_NOTE = (
    "この記事は WordPress 上で「ブログ」と「しごと情報」の両方のカテゴリが設定されていたため、"
    "自動振り分けができませんでした。内容を確認し、blog または job の適切な場所へ移動してください。"
)


def _wp_date_to_iso(post_date_gmt: str) -> str | None:
    if not post_date_gmt:
        return None
    try:
        dt = datetime.strptime(post_date_gmt, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_front_matter(item: WPItem, kind: str) -> dict:
    data: dict = {
        "title": item.title or f"(無題 - WordPress ID {item.post_id})",
    }

    date = _wp_date_to_iso(item.post_date_gmt)
    if date:
        data["date"] = date

    data["draft"] = item.status != "publish"

    if kind in CATEGORY_LABELS:
        data["categories"] = CATEGORY_LABELS[kind]

    data["wordpress_id"] = item.post_id

    if item.post_name:
        # Hugo は front matter の `slug` キーを URL 生成に使用してしまうため、
        # `job/nnnn.html` のようにファイル名 (WordPress の投稿 ID) を URL に使わせるよう、
        # WordPress のスラッグは別名の `wordpress_slug` として保持する。
        data["wordpress_slug"] = unquote(item.post_name)

    if item.link:
        data["source_url"] = item.link

    if kind == KIND_ERRORS:
        data["wordpress_import_error"] = ERROR_NOTE

    return data


def render_markdown_file(item: WPItem, kind: str, markdown_body: str) -> str:
    front_matter = build_front_matter(item, kind)
    front_matter_text = yaml.safe_dump(
        front_matter, allow_unicode=True, sort_keys=False
    )
    body = markdown_body.strip()
    return f"---\n{front_matter_text}---\n\n{body}\n"
