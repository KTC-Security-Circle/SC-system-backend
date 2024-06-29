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
京都テックSCシステムのバックエンドAPI
LangChainを使用したAgentsも導入予定

## 使用技術
- Python 3.10
- FastAPI

## 開発環境のセットアップ
1. githubからローカル環境に`git clone`してくる。
2. Pythonの仮想環境を作成します：`.venv`という名前のディレクトリが推奨されます。
3. Pythonのバージョンは3.10系で開発しています。
4. 仮想環境を有効にします。
5. `requirements.txt`にリストされているパッケージをインストールします。
6. rootディレクトリに`local.settings.json`というファイルを作成し、次のコードをコピペで入れます。
   ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "AzureWebJobsFeatureFlags": "EnableWorkerIndexing"
      }
    }
    ```
7. VSCodeの拡張機能である[Azure Tools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)をインストールする。


## ローカルでの実行方法
1. VSCode上で`F5`か実行とデバックからデバックを実行すると [http://localhost:7071/](http://localhost:7071/) でアクセスできるようになる。

## デプロイ方法
1. releaseブランチにマージすることでデプロイされます。(ほかメンバーに許可なくやらないこと)

## コントリビューション
