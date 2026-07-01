#!/usr/bin/env python3
"""WordPress のエクスポート XML (WordPress.xml) を Hugo 用の Markdown コンテンツへ変換するツール。

使い方は tools/import_wordpress.md を参照してください。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wpimport.assets import AssetManager  # noqa: E402
from wpimport.classify import (  # noqa: E402
    KIND_DIR,
    classify_item,
    output_path,
    public_url,
)
from wpimport.content import LOCAL_NUMBERED_KINDS, ContentProcessor  # noqa: E402
from wpimport.parser import parse_items  # noqa: E402
from wpimport.writer import render_markdown_file  # noqa: E402

KIND_ORDER = ["blog", "job", "pages", "contact", "errors"]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        default="migration/imports/WordPress.xml",
        help="WordPress からエクスポートした XML ファイルのパス (既定: migration/imports/WordPress.xml)",
    )
    parser.add_argument(
        "--output",
        default="src",
        help="Hugo の contentDir に相当する出力先ディレクトリ (既定: src)",
    )
    parser.add_argument(
        "--base-url",
        default="https://computer-union.jp",
        help="移行元サイトのベース URL (既定: https://computer-union.jp)",
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="画像・添付ファイルのダウンロードをスキップする (Markdown ファイルのみ生成)",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="出力先ディレクトリ (blog/job/pages/errors/images/contact.md) を事前に削除しない",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="ファイルを書き出さずに、分類結果の集計のみ表示する",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="動作確認用に、処理する記事数を先頭から N 件に制限する",
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

    if not input_path.exists():
        print(f"error: 入力ファイルが見つかりません: {input_path}", file=sys.stderr)
        return 1

    items = parse_items(input_path)

    classified: list[tuple] = []
    for item in items:
        kind = classify_item(item)
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

    if not args.dry_run and not args.no_clean:
        clean_output(output_root)

    asset_manager = AssetManager(download=not args.no_download)
    processor = ContentProcessor(args.base_url, asset_manager, url_map)

    counts: dict[str, int] = {}
    error_items: list[tuple[int, str]] = []

    for item, kind in classified:
        counts[kind] = counts.get(kind, 0) + 1
        dest_path = output_path(kind, item.post_id, output_root)
        image_dir = (
            dest_path.parent if kind in LOCAL_NUMBERED_KINDS else output_root / "images"
        )

        markdown_body = processor.process(
            item.content_html, kind, item.post_id, image_dir
        )
        file_text = render_markdown_file(item, kind, markdown_body)

        if kind == "errors":
            error_items.append((item.post_id, item.title))

        if not args.dry_run:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_text(file_text, encoding="utf-8")

    print("=== インポート結果 ===")
    for kind in KIND_ORDER:
        print(f"  {kind}: {counts.get(kind, 0)} 件")

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
