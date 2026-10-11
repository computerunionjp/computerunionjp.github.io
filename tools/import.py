from __future__ import annotations

import os
import re
import shutil


def get_project_dir() -> str:
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(tools_dir)


def get_next_id(project_dir: str) -> int:
    names: list[str] = []
    for dir in ["blog", "job"]:
        target = os.path.join(project_dir, "content", dir)
        if not os.path.isdir(target):
            continue
        entries = os.listdir(target)
        for entry in entries:
            if os.path.isdir(os.path.join(target, entry)):
                names.append(entry)
            else:
                names.append(os.path.splitext(entry)[0])

    ids = [int(s) for s in names if s.isdigit()]
    if not ids:
        return 1
    return max(ids) + 1


def read_categories(path: str) -> list[str]:
    """draft の .md ファイルの Front Matter から categories を取得する。"""
    categories: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or lines[0].strip() != "---":
        return categories

    in_categories = False
    for line in lines[1:]:
        stripped = line.rstrip("\n")
        if stripped.strip() == "---":
            break
        if re.match(r"^categories\s*:\s*$", stripped):
            in_categories = True
            continue
        if in_categories:
            m = re.match(r"^\s*-\s*(.+?)\s*$", stripped)
            if m:
                categories.append(m.group(1).strip("'\""))
                continue
            else:
                in_categories = False
        if re.match(r"^\S", stripped) and in_categories is False:
            # 次のキーに到達したら categories の読み取りを終了
            continue

    return categories


def category_to_key(categories: list[str]) -> str | None:
    if "しごと情報" in categories:
        return "job"
    if "ブログ" in categories:
        return "blog"
    return None


def import_file(src_path: str, project_dir: str, image: bool) -> str | None:
    categories = read_categories(src_path)
    key = category_to_key(categories)
    if key is None:
        print(f"{src_path} のカテゴリを判定できません。スキップします。")
        return None

    next_id = get_next_id(project_dir)

    if key == "blog" and image:
        relative_path = os.path.join("content", "blog", f"{next_id}", "index.md")
    else:
        relative_path = os.path.join("content", key, f"{next_id}.md")

    dest_path = os.path.join(project_dir, relative_path)
    base_path = os.path.dirname(dest_path)
    os.makedirs(base_path, exist_ok=True)

    _ = shutil.copyfile(src_path, dest_path)
    os.remove(src_path)

    rel_src = os.path.relpath(src_path, project_dir)
    print(f"{rel_src} を {relative_path} としてインポートしました。")

    return base_path


def match_images_to_md(
    md_files: list[str], other_files: list[str]
) -> tuple[dict[str, list[str]], list[str]]:
    """*.md 以外のファイルを、ファイル名が一致する *.md に割り当てる。

    "<mdのファイル名（拡張子無し）>-" または "<mdのファイル名（拡張子無
    し）>_" で始まるファイル名を、その *.md の添付ファイルとみなす。複数
    の *.md にマッチしうる場合は、より長く一致する（＝より具体的な）
    *.md を優先する。どの *.md にもマッチしないファイルは対象外として
    返す。
    """
    stems = sorted(
        (os.path.splitext(name)[0] for name in md_files),
        key=len,
        reverse=True,
    )

    matched: dict[str, list[str]] = {stem: [] for stem in stems}
    unmatched: list[str] = []

    for name in other_files:
        stem = os.path.splitext(name)[0]
        for md_stem in stems:
            if stem.startswith((md_stem + "-", md_stem + "_")):
                matched[md_stem].append(name)
                break
        else:
            unmatched.append(name)

    return matched, unmatched


def ask_skip_unmatched(unmatched: list[str]) -> bool:
    print("対象外のファイル:", ", ".join(unmatched))
    while True:
        choice = (
            input("これらのファイルをスキップしてインポートを続行しますか？ [Y/n]: ")
            .strip()
            .lower()
        )
        if choice in ("", "y"):
            return True
        if choice == "n":
            return False
        print("Y または n を入力してください。")


def ask_blog_image() -> bool:
    print("ブログの記事を取り込みます。")
    print("  2. ブログ（画像無し）")
    print("  3. ブログ（画像有り）")

    while True:
        choice = input("番号を入力してください (2～3): ").strip()
        if choice == "2":
            return False
        if choice == "3":
            return True
        print("2 または 3 を入力してください。")


def main() -> None:
    project_dir = get_project_dir()
    drafts_dir = os.path.join(project_dir, "drafts")

    if not os.path.isdir(drafts_dir):
        print(f"{drafts_dir} が見つかりません。処理を中止します。")
        return

    entries = sorted(os.listdir(drafts_dir))
    entries = [e for e in entries if not e.startswith(".")]

    if not entries:
        print("drafts/ にファイルがありません。処理を中止します。")
        return

    md_files = [e for e in entries if e.lower().endswith(".md")]
    other_files = [e for e in entries if not e.lower().endswith(".md")]

    if other_files:
        if not md_files:
            print(
                "drafts/ に *.md 以外のファイルが含まれているため、処理を中止します。"
            )
            print("対象外のファイル:", ", ".join(other_files))
            return

        matched, unmatched = match_images_to_md(md_files, other_files)

        skip_files: list[str] = []
        if unmatched:
            print("drafts/ に *.md 以外のファイルが含まれています。")
            if not ask_skip_unmatched(unmatched):
                print("処理を中止します。")
                return
            skip_files = unmatched

        # 添付ファイルを持つ *.md はブログのみ対応。
        for name in md_files:
            stem = os.path.splitext(name)[0]
            if matched[stem]:
                src_path = os.path.join(drafts_dir, name)
                categories = read_categories(src_path)
                if "ブログ" not in categories:
                    print(
                        f"{name} はブログ以外のカテゴリのため、画像などの添付ファイルをインポートできません。処理を中止します。"
                    )
                    return

        for name in md_files:
            stem = os.path.splitext(name)[0]
            src_path = os.path.join(drafts_dir, name)
            images = matched[stem]
            base_path = import_file(src_path, project_dir, image=bool(images))
            if base_path is not None:
                for image_name in images:
                    other_src = os.path.join(drafts_dir, image_name)
                    other_dest = os.path.join(base_path, image_name)
                    _ = shutil.move(other_src, other_dest)
                    rel_src = os.path.relpath(other_src, project_dir)
                    rel_dest = os.path.relpath(other_dest, project_dir)
                    print(f"{rel_src} を {rel_dest} に移動しました。")

        if skip_files:
            for name in skip_files:
                skip_path = os.path.join(drafts_dir, name)
                os.remove(skip_path)
                rel_path = os.path.relpath(skip_path, project_dir)
                print(f"{rel_path} を削除しました。")
        return

    if not md_files:
        print("drafts/ に *.md ファイルがありません。処理を中止します。")
        return

    if len(md_files) == 1:
        src_path = os.path.join(drafts_dir, md_files[0])
        categories = read_categories(src_path)

        if "ブログ" in categories:
            image = ask_blog_image()
            _ = import_file(src_path, project_dir, image)
            return

        # ブログ以外（しごと情報など）はカテゴリに応じて自動判定する。
        _ = import_file(src_path, project_dir, image=False)
        return

    # drafts/ に複数の *.md ファイルのみが存在する場合は、
    # 各ファイルのカテゴリに応じて自動的に取り込み先を決定する。
    for name in md_files:
        src_path = os.path.join(drafts_dir, name)
        _ = import_file(src_path, project_dir, image=False)


if __name__ == "__main__":
    main()
