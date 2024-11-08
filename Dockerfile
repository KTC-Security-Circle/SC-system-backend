FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# git等を使えるように設定
RUN apt-get update && apt-get install -y \
git \
sudo \
curl \
azure-functions-core-tools-4 \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

RUN git config --global --add safe.directory /app


# ユーザーIDとグループIDをビルド時の引数として受け取る
ARG USER_ID=1000
ARG GROUP_ID=1000

# ユーザーとグループを作成
RUN groupadd -g ${GROUP_ID} appgroup && \
useradd -m -d /home/appuser -s /bin/bash -u ${USER_ID} -g appgroup appuser && \
echo 'appuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ENV HOME=/home/appuser
USER appuser

# 作業ディレクトリを設定
WORKDIR /app

RUN pip install --upgrade pip

# poetryのインストール、設定
RUN pip install --upgrade pip && pip install poetry 
ENV PATH="/home/appuser/.local/bin:$PATH"

# Azure Functionsの設定
ENV AzureWebJobsScriptRoot=/workspaces \
AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# # poetryでinstallしているのでコメントアウト
# # COPY requirements.txt /
# # RUN pip install -r /requirements.txt

# COPY . /home/site/wwwroot




# アプリケーションコードをコピー
COPY --chown=appuser:appgroup . /app