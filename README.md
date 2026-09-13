# ほいくのあき（仮）

東京都内の保育園空き状況を自治体オープンデータから集約する静的サイトのMVP。
まずは杉並区（CC-BYライセンスのオープンデータ）から開始。

## ディレクトリ構成

```
scripts/               データ取得・パース用Pythonスクリプト
data/suginami.json      正規化済みデータ（GitHub Actionsが自動更新）
site/index.html          表示用の静的サイト本体
.github/workflows/       月1回の自動データ更新ジョブ
requirements.txt         Python依存パッケージ
```

## セットアップ手順

1. このリポジトリをGitHubにpush
2. GitHubリポジトリの **Settings → Pages** で、
   - Source: `Deploy from a branch`
   - Branch: `main` / フォルダ: `/site` ※GitHub Pagesの仕様上、
     ルート直下かdocsフォルダのみ選べる場合があるため、
     `site/` を公開したい場合はビルド用ワークフローで
     `docs/` にコピーするか、Pages用ブランチを分ける方法が簡単です。
     （まずは `site/index.html` の中身を確認しながら調整してください）
3. `.github/workflows/update-data.yml` により、毎月1日にデータが自動更新されます
   - 手動で今すぐ実行したい場合は、GitHubの Actions タブから
     「Update Suginami Childcare Data」→「Run workflow」で即実行できます
4. ローカルで試す場合:
   ```bash
   pip install -r requirements.txt
   python scripts/suginami_parser.py
   ```
   実行後、`data/suginami.json` が最新化されます。

## 注意事項

- `scripts/suginami_parser.py` の `COLUMN_MAP` は実データを見て
  列構成のズレがないか都度確認してください
  （実行時に実際の列名一覧が標準出力に表示されます）
- CSVの直リンクURLは月ごとにファイル名が変わるため、将来的には
  カタログページから最新リンクを自動取得するロジックへの拡張を推奨します
- サイトには「参考情報であり、正確性は保証しない」旨の免責文言を
  必ず掲載してください（`site/index.html` に組み込み済み）
