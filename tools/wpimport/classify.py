"""記事・固定ページを移行先の種別 (blog / job / pages / contact / errors) に分類する。"""

from __future__ import annotations

from pathlib import Path

from .parser import WPItem

CATEGORY_BLOG = "blog"
CATEGORY_OFFERS = "offers"

CONTACT_TITLE = "お問い合わせ"

# WordPress の投稿 ID がこの値より小さい記事・固定ページ (post_type == "post" / "page") は
# 移行対象外とする
MIN_POST_ID = 3500

KIND_BLOG = "blog"
KIND_JOB = "job"
KIND_PAGES = "pages"
KIND_CONTACT = "contact"
KIND_ERRORS = "errors"

# 出力先ディレクトリ名 (contact は単一ファイルなので対象外)
KIND_DIR = {
    KIND_BLOG: "blog",
    KIND_JOB: "job",
    KIND_PAGES: "pages",
    KIND_ERRORS: "errors",
}


def classify_item(item: WPItem) -> str | None:
    """WPItem を分類する。移行対象外の場合は None を返す。"""
    if item.post_type not in ("post", "page"):
        # post / page 以外 (attachment, nav_menu_item, wp_template, ...) は移行対象外
        return None

    if item.post_id < MIN_POST_ID:
        # 古い投稿・固定ページ (ID が MIN_POST_ID 未満) は移行対象外とする
        return None

    if item.post_type == "post":
        nicenames = item.category_nicenames("category")
        has_blog = CATEGORY_BLOG in nicenames
        has_offers = CATEGORY_OFFERS in nicenames
        if has_blog and has_offers:
            return KIND_ERRORS
        if has_blog:
            return KIND_BLOG
        if has_offers:
            return KIND_JOB
        # ブログでもしごと情報でもないカテゴリの記事は「トップページ以外のページ」として扱う
        return KIND_PAGES

    # item.post_type == "page"
    if item.title.strip() == CONTACT_TITLE:
        return KIND_CONTACT
    return KIND_PAGES


def output_path(kind: str, post_id: int, output_root: Path) -> Path:
    if kind == KIND_CONTACT:
        return output_root / "contact.md"
    return output_root / KIND_DIR[kind] / f"{post_id}.md"


def public_url(kind: str, post_id: int) -> str:
    """Hugo の既定 (pretty URL) での公開 URL を返す。"""
    if kind == KIND_CONTACT:
        return "/contact/"
    return f"/{KIND_DIR[kind]}/{post_id}/"
