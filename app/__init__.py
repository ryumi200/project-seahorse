from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Flaskアプリケーションを初期化
app = Flask(__name__)

# データベース設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///task.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemyインスタンスを作成
db = SQLAlchemy(app)

# ルートをインポート
from app import routes
