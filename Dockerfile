#ベースイメージとしてpython3.9を使用
FROM python:3.9-slim-buster

#作業ディレクトリを設定
WORKDIR /app

#必要なパッケージをインストール
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

#アプリケーションのコードをコピー
COPY . .

#ポート5000を開放
EXPOSE 5000

#アプリケーションを実行
CMD ["python", "run.py"]