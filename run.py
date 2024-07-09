from app import app, db

if __name__ == "__main__":
    # アプリケーション実行前にデータベースを作成
    with app.app_context():
        db.create_all()

    # アプリケーションを実行(デバッグモードで)
    app.run(debug=True, host="0.0.0.0")
