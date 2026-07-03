"""WordPress の本文 (HTML) を、画像・リンクをローカル参照に置き換えたうえで Markdown に変換する。"""

from __future__ import annotations

import html
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

# Material Icons のリガチャ (<span class="material-icons">open_in_new</span> など) を
# 実際のアイコン画像に置き換えるための情報。ダウンロード元は移行元サイトに実在する
# 添付ファイル (wp:post_name: external_link / outline_folder_black_24dp) の URL。
EXTERNAL_LINK_ICON_SRC = "/wp-content/uploads/2021/07/external_link.png"
EXTERNAL_LINK_ICON_PATH = "/images/external_link.png"
FOLDER_ICON_SRC = "/wp-content/uploads/2021/07/outline_folder_black_24dp.png"
FOLDER_ICON_PATH = "/images/outline_folder_black_24dp.png"

# Gutenberg の "最新の投稿" ブロック (<!-- wp:latest-posts {"categories":[{"id":N,...}]} /-->) は
# WordPress が表示時に動的生成するため、エクスポートには静的な HTML が含まれていない。
# 対応するカテゴリの最新 5 件を Hugo のショートコードで動的に埋め込むプレースホルダに置き換える。
LATEST_POSTS_COMMENT_RE = re.compile(
    r'wp:latest-posts\s*\{.*?"id"\s*:\s*(\d+)', re.DOTALL
)
LATEST_POSTS_SECTIONS = {
    5: "job",  # 「しごと情報」 (nicename: offers)
    10: "blog",  # 「ブログ」 (nicename: blog)
}
LATEST_POSTS_COUNT = 5


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


def _material_icon_names(anchor) -> set[str]:
    return {
        span.get_text(strip=True)
        for span in anchor.find_all("span", class_="material-icons")
    }


def _remove_material_icon_spans(anchor) -> None:
    for span in anchor.find_all("span", class_="material-icons"):
        if not getattr(span, "decomposed", False):
            span.decompose()


def _latest_posts_shortcode(comment_text: str) -> str | None:
    """wp:latest-posts ブロックコメントを、対応する Hugo ショートコード呼び出しに変換する。
    対象外のコメントや未知のカテゴリの場合は None を返す。
    """
    if "wp:latest-posts" not in comment_text:
        return None
    match = LATEST_POSTS_COMMENT_RE.search(comment_text)
    if not match:
        return None
    category_id = int(match.group(1))
    section = LATEST_POSTS_SECTIONS.get(category_id)
    if section is None:
        return None
    return f'{{{{< latest-posts section="{section}" count="{LATEST_POSTS_COUNT}" >}}}}'


class ContentProcessor:
    """WPItem 本文の HTML を Markdown へ変換するクラス。"""

    def __init__(
        self,
        base_url: str,
        asset_manager: AssetManager,
        url_map: dict[int, str],
        asset_base_url: str | None = None,
        contact_post_id: int | None = None,
        contact_override_url: str | None = None,
        shared_images_dir: Path | None = None,
    ):
        # base_url: 本文中の絶対 URL リンクが「自分自身へのリンク」かどうかを
        # 判定するためのベース URL (テストモードではテスト用のドメインになる)。
        self.base_url = base_url
        # asset_base_url: 相対パスの画像・添付ファイル URL を解決する際に使うベース URL。
        # 画像は常に移行元の実サイトから取得する必要があるため、base_url とは独立にする。
        self.asset_base_url = asset_base_url or base_url
        self.asset_manager = asset_manager
        self.url_map = url_map
        # テストモードで「お問い合わせ」へのリンクを特別扱いするための情報。
        self.contact_post_id = contact_post_id
        self.contact_override_url = contact_override_url
        # Material Icons の置き換え画像 (open_in_new / folder) の保存先。
        # 記事の種別に関わらず常に共有の images ディレクトリに配置する。
        self.shared_images_dir = shared_images_dir

    def _resolve_href(
        self, href: str, kind: str, post_id: int, image_dest_dir: Path, local_asset_ref
    ) -> str:
        if _is_upload_url(href):
            return local_asset_ref(href)
        if _is_internal_link(href, self.base_url):
            referenced_id = _extract_referenced_post_id(href)
            category_id = _extract_category_id(href)
            if (
                self.contact_post_id is not None
                and referenced_id == self.contact_post_id
                and self.contact_override_url
            ):
                # テストモードでは「お問い合わせ」へのリンクを、ローカルの /contact/ ではなく
                # 移行元サイトの実際のお問い合わせページへの絶対 URL にする
                return self.contact_override_url
            if referenced_id is not None and referenced_id in self.url_map:
                return self.url_map[referenced_id]
            if category_id is not None and category_id in CATEGORY_ARCHIVE_URLS:
                return CATEGORY_ARCHIVE_URLS[category_id]
        return href

    def _download_shared_icon(self, relative_src: str, filename: str) -> None:
        if self.shared_images_dir is None:
            return
        absolute_url = urljoin(self.asset_base_url, relative_src)
        self.asset_manager.save(absolute_url, self.shared_images_dir / filename)

    def process(
        self, html_text: str, kind: str, post_id: int, image_dest_dir: Path
    ) -> tuple[str, bool]:
        """HTML を Markdown に変換する。

        戻り値は (markdown_text, has_bundle_assets) のタプル。
        has_bundle_assets は、kind が LOCAL_NUMBERED_KINDS の場合に、記事本文中に
        ローカル番号付きで配置すべき画像・添付ファイルが 1 つ以上あったかどうかを示す
        (Page Bundle にすべきかの判断に使う)。
        """
        soup = BeautifulSoup(html_text or "", "html.parser")

        # Gutenberg のブロックコメント (<!-- wp:xxx --> など) を含む HTML コメントを除去。
        # ただし wp:latest-posts ブロックは、Hugo ショートコードの呼び出しに置き換える。
        html_placeholders: dict[str, str] = {}
        placeholder_counter = {"n": 0}

        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            shortcode = _latest_posts_shortcode(str(comment))
            if shortcode:
                placeholder_counter["n"] += 1
                placeholder = f"ZZWPIMPORTHTML{placeholder_counter['n']}ZZ"
                html_placeholders[placeholder] = shortcode
                comment.replace_with(placeholder)
            else:
                comment.extract()

        local_refs: dict[str, str] = {}
        counter = {"n": 0}
        has_bundle_assets = {"flag": False}

        def local_asset_ref(url: str) -> str:
            if url in local_refs:
                return local_refs[url]
            counter["n"] += 1
            basename = url.split("?", 1)[0].rsplit("/", 1)[-1]
            ext = basename.rsplit(".", 1)[-1].lower() if "." in basename else "jpg"
            if kind in LOCAL_NUMBERED_KINDS:
                filename = f"{post_id}_{counter['n']:03d}.{ext}"
                # この種別の記事は Page Bundle (例: blog/{id}/index.md) として出力されるため、
                # 画像は index.md と同じディレクトリに配置される。相対ファイル名で参照すればよい。
                ref = filename
                has_bundle_assets["flag"] = True
            else:
                filename = basename
                ref = f"/images/{filename}"
            absolute_url = urljoin(self.asset_base_url, url)
            self.asset_manager.save(absolute_url, image_dest_dir / filename)
            local_refs[url] = ref
            return ref

        for img in soup.find_all("img"):
            src = img.get("src")
            if src and _is_upload_url(src):
                img["src"] = local_asset_ref(src)

        # <a> タグに埋め込まれた Material Icons のリガチャ文字列 (open_in_new / folder) を、
        # 実際のアイコン画像に置き換える。open_in_new は target/rel を維持する必要があるため
        # Markdown 変換をバイパスして生の HTML のまま埋め込む (上で作成したプレースホルダを共用する)。
        for anchor in soup.find_all("a"):
            href = anchor.get("href")
            icon_names = _material_icon_names(anchor)

            if "open_in_new" in icon_names:
                resolved_href = (
                    self._resolve_href(
                        href, kind, post_id, image_dest_dir, local_asset_ref
                    )
                    if href
                    else href
                )
                _remove_material_icon_spans(anchor)
                text = anchor.get_text()
                self._download_shared_icon(EXTERNAL_LINK_ICON_SRC, "external_link.png")
                raw_html = (
                    f'<a href="{html.escape(resolved_href or "")}" '
                    'target="_blank" rel="noopener noreferrer">'
                    f"{html.escape(text)}"
                    f'<span class="material-symbols-outlined">open_in_new</span></a>'
                )
                placeholder_counter["n"] += 1
                placeholder = f"ZZWPIMPORTHTML{placeholder_counter['n']}ZZ"
                html_placeholders[placeholder] = raw_html
                anchor.replace_with(placeholder)
                continue

            if "folder" in icon_names:
                for span in anchor.find_all("span", class_="material-icons"):
                    if getattr(span, "decomposed", False):
                        continue
                    if span.get_text(strip=True) != "folder":
                        continue
                    img_tag = soup.new_tag("img", src=FOLDER_ICON_PATH, alt="Folder")
                    span.replace_with(img_tag)
                    img_tag.insert_after(" ")
                self._download_shared_icon(
                    FOLDER_ICON_SRC, "outline_folder_black_24dp.png"
                )

            if href:
                anchor["href"] = self._resolve_href(
                    href, kind, post_id, image_dest_dir, local_asset_ref
                )

        cleaned_html = str(soup)
        markdown_text = html_to_markdown(
            cleaned_html,
            heading_style="ATX",
            bullets="-",
            strip=["script", "style"],
            keep_inline_images_in=["a"],
        )

        for placeholder, raw_html in html_placeholders.items():
            markdown_text = markdown_text.replace(placeholder, raw_html)

        markdown_text = re.sub(r"\n{3,}", "\n\n", markdown_text.strip()) + "\n"

        if kind == KIND_JOB:
            markdown_text = _fix_job_table_headers(markdown_text)

        return markdown_text, has_bundle_assets["flag"]
