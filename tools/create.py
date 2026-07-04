import os
from datetime import datetime


def main():
    print(
        "記事の種類を選択してください。中止する場合は何も入力せずに Enter を押してください。"
    )
    print("  1. しごと情報")
    print("  2. ブログ（画像無し）")
    print("  3. ブログ（画像有り）")

    choice = input("番号を入力してください (1～3): ")

    category = ""
    image = None

    if choice == "1":
        print("しごと情報を選択しました。")
        category = "job"
        image = False
    elif choice == "2":
        print("ブログ（画像無し）を選択しました。")
        category = "blog"
        image = False
    elif choice == "3":
        print("ブログ（画像有り）を選択しました。")
        category = "blog"
        image = True
    else:
        print("無効な番号です。")

    names: list[str] = []
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tools_dir)

    for dir in ["blog", "job", "pages"]:
        target = os.path.join(project_dir, "src", dir)
        entries = os.listdir(target)
        for entry in entries:
            if os.path.isdir(os.path.join(target, entry)):
                names.append(entry)
            else:
                names.append(os.path.splitext(entry)[0])

    ids = [s for s in names if s.isdigit()]
    ids.sort(reverse=True)
    id = int(ids[0]) + 1

    relative_path = (
        os.path.join("src", category, f"{id}", "index.md")
        if image
        else os.path.join("src", category, f"{id}.md")
    )
    dest_path = os.path.join(project_dir, relative_path)
    tmpl_path = os.path.join(tools_dir, f"template_{category}.md")

    while True:
        print(f"{relative_path} を作成します。")
        answer = input("実行しますか？ [Y/n]: ").strip()

        if answer == "":
            answer = "Y"

        answer = answer.upper()

        if answer == "Y":
            base_path = os.path.dirname(dest_path)
            os.makedirs(base_path, exist_ok=True)

            now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            with (
                open(tmpl_path, "r", encoding="utf-8") as tmpl,
                open(dest_path, "w", encoding="utf-8") as dest,
            ):
                for line in tmpl:
                    if line.startswith("date:"):
                        _ = dest.write(f"date: '{now}'\n")
                    else:
                        _ = dest.write(line)
            break
        elif answer == "N":
            print("処理を中止します。")
            break
        else:
            print("Y または N を入力してください。")


if __name__ == "__main__":
    main()
