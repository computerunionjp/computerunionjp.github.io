# computer-union.jp

準備中

ローカルでプレビューするには `hugo` が必要です。

```bash
hugo server
```

`src` の下を更新すると自動で GitHub Actions
によりサイトに反映されます。反映には数十秒かかります。
GitHub Actions の設定は `.github/workflows/on-push.yaml`
を参照してください。

下記のディレクトリは GitHub Actions で無視する設定にしています。作業のマニュアルやコンテンツ作成のための補助的なツール等を置いてください。

- docs/
- migration/
- test/
- tools/
