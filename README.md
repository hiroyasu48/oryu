# oryu - Website Change Monitor

[31sumai.com/attend/X2571](https://www.31sumai.com/attend/X2571/) のサイト変更を監視し、変更があればDiscordに通知するシステムです。

GitHub Actionsを使って**1時間ごと**に自動チェックします。

## セットアップ

### 1. Discord Webhook URLを取得する

1. Discordを開き、通知を受け取りたいサーバーのチャンネルを選ぶ
2. チャンネル名を右クリック → **「チャンネルを編集」**
3. **「連携サービス」** → **「ウェブフック」** → **「新しいウェブフック」**
4. 名前を設定し、**「ウェブフックURLをコピー」** をクリック

### 2. GitHubにSecretを設定する

1. GitHubリポジトリの **Settings** を開く
2. **Secrets and variables** → **Actions** → **「New repository secret」**
3. 以下を設定する：
   - Name: `DISCORD_WEBHOOK_URL`
   - Secret: コピーしたWebhook URL

### 3. GitHub Actionsを有効化する

リポジトリの **Actions** タブを開き、ワークフローを有効化する。

これで設定完了です。以降は1時間ごとに自動チェックされます。

---

## 動作確認（手動実行）

GitHub Actions の **Actions** タブ → **Website Change Monitor** → **Run workflow** で手動実行できます。

## ローカルで実行する場合

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数を設定
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

# 実行
python monitor.py
```

## 監視頻度の変更

`.github/workflows/monitor.yml` の `cron` を変更します。

```yaml
schedule:
  - cron: '0 * * * *'   # 毎時（デフォルト）
  - cron: '0 */3 * * *' # 3時間ごと
  - cron: '0 9 * * *'   # 毎日9時（UTC）= 日本時間18時
```

## ファイル構成

```
.
├── monitor.py                    # 監視スクリプト
├── requirements.txt              # Pythonパッケージ
├── state.json                    # 最終チェック時の状態（自動生成）
├── .env.example                  # 環境変数のサンプル
└── .github/workflows/monitor.yml # GitHub Actionsワークフロー
```
