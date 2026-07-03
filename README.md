# computer-union.jp

## 編集

`src` の下を更新すると自動で GitHub Actions　によりサイトに反映されます。反映には数十秒かかります。

- src
    - blog
        - 5848.md -- ブログの原稿(1) 画像無し
        - 7251 -- ブログの原稿(2) 画像有り
            - index.md
            - 7251_001.png
            - 7251_002.png
    - job
        - 8065.md -- しごと情報の原稿

Visual Studio Code など Markdown の編集と GitHub の操作に対応したツールの利用をお勧めします。

ローカルでプレビューするには `hugo` が必要です。

```bash
git clone https://github.com/computerunionjp/computerunionjp.git
cd computerunionjp
hugo server
```

## 記事のサンプル

- sample
    - blog
        - 5848.md -- ブログのサンプル(1) 画像無し
        - 7251 -- ブログのサンプル(2) 画像有り
            - index.md
            - 7251_001.png
            - 7251_002.png
    - job
        - 8065.md -- しごと情報のサンプル

## 開発

GitHub Actions の設定は `.github/workflows/on-push.yaml`　を参照してください。

下記のディレクトリは GitHub Actions で無視する設定にしています。作業のマニュアルやコンテンツ作成のための補助的なツール等を置いてください。

- docs/
- migration/
- test/
- tools/

[移行ツールの使い方](tools/import_wordpress.md)
