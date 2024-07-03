# SC-system-backend

## 目次

- [SC-system-backend](#sc-system-backend)
  - [目次](#目次)
  - [プロジェクトの概要](#プロジェクトの概要)
  - [使用技術](#使用技術)
  - [開発環境のセットアップ](#開発環境のセットアップ)
  - [ローカルでの実行方法](#ローカルでの実行方法)
  - [デプロイ方法](#デプロイ方法)
  - [コントリビューション](#コントリビューション)

## プロジェクトの概要

京都テック SC システムのバックエンド API
LangChain を使用した Agents も導入予定

## 使用技術

- Python 3.10
- FastAPI

## 開発環境のセットアップ

1. github からローカル環境に`git clone`してくる。
2. Python の仮想環境を作成します：`.venv`という名前のディレクトリが推奨されます。
3. Python のバージョンは 3.10 系で開発しています。
4. 仮想環境を有効にします。
5. `requirements.txt`にリストされているパッケージをインストールします。
6. root ディレクトリに`local.settings.json`というファイルを作成し、次のコードをコピペで入れます。
   ```json
   {
     "IsEncrypted": false,
     "Values": {
       "AzureWebJobsStorage": "",
       "FUNCTIONS_WORKER_RUNTIME": "python",
       "AzureWebJobsFeatureFlags": "EnableWorkerIndexing"
     },
     "Host": {
       "CORS": "*"
     }
   }
   ```
7. VSCode の拡張機能である[Azure Tools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)をインストールする。

## ローカルでの実行方法

1. VSCode 上で`F5`か実行とデバックからデバックを実行すると [http://localhost:7071/](http://localhost:7071/) でアクセスできるようになる。

## デプロイ方法

1. release ブランチにマージすることでデプロイされます。(ほかメンバーに許可なくやらないこと)

## コントリビューション
