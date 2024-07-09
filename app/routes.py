from flask import render_template, request, redirect, url_for
from app import app, db
from app.models import Task


@app.route("/")
def index():
    # すべてのタスクを取得し、作成日時の降順で並び替え
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        # フォームからデータを取得
        title = request.form["title"]
        description = request.form["description"]

        # 新しいタスクを作成
        new_task = Task(title=title, description=description)

        # データベースに追加して保存
        db.session.add(new_task)
        db.session.commit()

        # タスク一覧ベージにリダイレクト
        return redirect(url_for("index"))

    # GETリクエストの場合、タスク追加フォームを表示
    return render_template("add_task.html")


@app.route("/complete/<int:id>")
def complete_task(id):
    # 指定されたタスクのIDを取得
    task = Task.query.get_or_404(id)

    # タスクの完了状態を切り替え
    task.completed = not task.completed

    # 変更を保存
    db.session.commit()

    # タスク一覧ページにリダイレクト
    return redirect(url_for("index"))
