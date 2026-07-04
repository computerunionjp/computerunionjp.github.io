#!/usr/bin/env python3
"""WordPress のエクスポート XML (WordPress.xml) を Hugo 用の Markdown コンテンツへ変換するツール。

使い方は tools/import_wordpress.md を参照してください。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .wpimport.assets import AssetManager
from .wpimport.classify import (
    KIND_DIR,
    MIN_POST_ID,
    classify_item,
    output_path,
    public_url,
)
from .wpimport.content import LOCAL_NUMBERED_KINDS, ContentProcessor
from .wpimport.parser import WPItem, parse_items
from .wpimport.writer import render_markdown_file

KIND_ORDER = ["blog", "job", "pages", "contact", "errors"]

# 本番の移行元サイト (画像・添付ファイルは常にここから取得する)
DEFAULT_BASE_URL = "https://computer-union.jp"

# --test 指定時 (または --dry-run / --limit 指定時) に仮定する --base-url の既定値
TEST_BASE_URL = "https://computerunionjp.github.io/"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument(
        "--input",
        default="migration/imports/WordPress.xml",
        help="WordPress からエクスポートした XML ファイルのパス (既定: migration/imports/WordPress.xml)",
    )
    _ = parser.add_argument(
        "--output",
        default="src",
        help="Hugo の contentDir に相当する出力先ディレクトリ (既定: src)",
    )
    _ = parser.add_argument(
        "--base-url",
        default=None,
        help=(
            "移行先サイト自身のベース URL (既定: 通常時は "
            f"{DEFAULT_BASE_URL} 、--test 指定時 (または後述のとおり --test が仮定される場合) は "
            f"{TEST_BASE_URL})"
        ),
    )
    _ = parser.add_argument(
        "--no-download",
        action="store_true",
        help="画像・添付ファイルのダウンロードをスキップする (Markdown ファイルのみ生成)",
    )
    _ = parser.add_argument(
        "--refresh",
        action="store_true",
        help=(
            "src の下の生成済みファイル (blog/job/pages/errors/images/contact.md) を事前に"
            "全て削除してから再インポートする。指定しない場合は削除を行わず、まだインポートしていない投稿 ID"
            "の記事・ページだけを追加する"
        ),
    )
    _ = parser.add_argument(
        "--start",
        type=int,
        default=None,
        help=(
            "この WordPress の投稿 ID より古い記事・固定ページを移行対象外とする "
            f"(既定: {MIN_POST_ID})"
        ),
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ファイルを書き出さずに、分類結果の集計のみ表示する (--test も仮定される)",
    )
    _ = parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="動作確認用に、処理する記事数を先頭から N 件に制限する (--test も仮定される)",
    )
    _ = parser.add_argument(
        "--test",
        action="store_true",
        help=(
            "テストモードで実行する。--base-url の既定値が "
            f"{TEST_BASE_URL} になり、本文中の「お問い合わせ」へのリンクは "
            "/contact/ ではなく移行元サイトの実際のお問い合わせページ URL になる"
        ),
    )
    return parser


def clean_output(output_root: Path) -> None:
    for dir_name in (*KIND_DIR.values(), "images"):
        target = output_root / dir_name
        if target.exists():
            shutil.rmtree(target)
    contact_file = output_root / "contact.md"
    if contact_file.exists():
        contact_file.unlink()


def main() -> int:
    args = build_arg_parser().parse_args()
    input_path = Path(args.input)
    output_root = Path(args.output)

    # --dry-run または --limit が指定された場合は --test も指定されているものとみなす。
    test_mode = args.test or args.dry_run or args.limit is not None
    base_url = args.base_url or (TEST_BASE_URL if test_mode else DEFAULT_BASE_URL)
    start_id = args.start if args.start is not None else MIN_POST_ID

    if not input_path.exists():
        print(f"error: 入力ファイルが見つかりません: {input_path}", file=sys.stderr)
        return 1

    items = parse_items(input_path)

    classified: list[tuple[WPItem, str]] = []
    for item in items:
        kind = classify_item(item, min_post_id=start_id)
        if kind is None:
            continue
        classified.append((item, kind))

    if args.limit is not None:
        classified = classified[: args.limit]

    # 内部リンク (?p=N / ?page_id=N) の付け替え用に、投稿・固定ページ ID から
    # 移行先の公開 URL への対応表を先に構築しておく。
    url_map = {
        item.post_id: public_url(kind, item.post_id) for item, kind in classified
    }

    if args.refresh and not args.dry_run:
        clean_output(output_root)

    # テストモードでは「お問い合わせ」へのリンクを、移行先の実際の URL に差し替える。
    contact_post_id = None
    contact_override_url = None
    if test_mode:
        for item, kind in classified:
            if kind == "contact":
                contact_post_id = item.post_id
                contact_override_url = item.link or None
                break

    asset_manager = AssetManager(download=not args.no_download)
    processor = ContentProcessor(
        base_url,
        asset_manager,
        url_map,
        asset_base_url=DEFAULT_BASE_URL,
        contact_post_id=contact_post_id,
        contact_override_url=contact_override_url,
        shared_images_dir=output_root / "images",
    )

    counts: dict[str, dict[str, int]] = {
        kind: {"total": 0, "new": 0, "existing": 0} for kind in KIND_ORDER
    }
    error_items: list[tuple[int, str]] = []
    new_items: list[tuple[int, str]] = []

    for item, kind in classified:
        counts[kind]["total"] += 1

        if kind == "errors":
            error_items.append((item.post_id, item.title))

        is_bundleable = kind in LOCAL_NUMBERED_KINDS
        bundle_path: Path | None = None
        flat_path: Path | None = None

        if is_bundleable:
            # 画像を含む可能性がある種別は、実際に画像があれば Page Bundle
            # (blog/{id}/index.md) 、なければ単一ファイル (blog/{id}.md) として出力する。
            # どちらになるかは本文を処理してみないと分からないため、既存判定は
            # 両方のパスを確認する。
            bundle_dir = output_root / KIND_DIR[kind] / str(item.post_id)
            bundle_path = bundle_dir / "index.md"
            flat_path = output_root / KIND_DIR[kind] / f"{item.post_id}.md"
            already_exists = bundle_path.exists() or flat_path.exists()
            image_dir = bundle_dir
        else:
            already_exists = output_path(kind, item.post_id, output_root).exists()
            image_dir = output_root / "images"

        # --refresh が指定されていない場合、既にインポート済み (出力ファイルが存在する)
        # の記事・ページは再処理せずスキップする (画像の再ダウンロードも行わない)。
        if already_exists and not args.refresh:
            counts[kind]["existing"] += 1
            continue

        counts[kind]["new"] += 1
        new_items.append((item.post_id, item.title))

        markdown_body, has_bundle_assets = processor.process(
            item.content_html, kind, item.post_id, image_dir
        )
        file_text = render_markdown_file(item, kind, markdown_body)

        if is_bundleable:
            assert bundle_path is not None and flat_path is not None
            dest_path = bundle_path if has_bundle_assets else flat_path
        else:
            dest_path = output_path(kind, item.post_id, output_root)

        if not args.dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(file_text, encoding="utf-8")

    print("=== インポート結果 ===")
    print(f"  test_mode: {test_mode} / base_url: {base_url}")
    print(f"  refresh: {args.refresh} / start_id: {start_id}")
    for kind in KIND_ORDER:
        c = counts[kind]
        print(
            f"  {kind}: {c['total']} 件 (新規 {c['new']} 件 / 既存 {c['existing']} 件)"
        )

    if new_items and not args.refresh:
        print(f"\n[+] 新たに追加された記事・ページ: {len(new_items)} 件")
        for post_id, title in new_items[:20]:
            print(f"    - {post_id}: {title}")
        if len(new_items) > 20:
            print(f"    ... 他 {len(new_items) - 20} 件")

    if error_items:
        print(
            "\n[!] src/errors に振り分けられた記事があります (「ブログ」と「しごと情報」の両方のカテゴリを持つため要手動確認):"
        )
        for post_id, title in error_items:
            print(f"    - {post_id}: {title}")

    if not args.no_download and asset_manager.failed:
        print(
            f"\n[!] ダウンロードに失敗した画像・添付ファイル: {len(asset_manager.failed)} 件"
        )
        for url, err in asset_manager.failed[:20]:
            print(f"    - {url} ({err})")
        if len(asset_manager.failed) > 20:
            print(f"    ... 他 {len(asset_manager.failed) - 20} 件")

    if args.dry_run:
        print("\n(--dry-run のため、ファイルの書き出しは行っていません)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
