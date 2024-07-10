from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from app.models import User, Task
from werkzeug.urls import url_parse


@app.route("/")
@login_required
def index():
    incomplete_tasks = (
        Task.query.filter_by(user_id=current_user.id, completed=False, is_deleted=False)
        .order_by(Task.created_at.desc())
        .all()
    )
    completed_tasks = (
        Task.query.filter_by(user_id=current_user.id, completed=True, is_deleted=False)
        .order_by(Task.created_at.desc())
        .all()
    )
    deleted_tasks = (
        Task.query.filter_by(user_id=current_user.id, is_deleted=True)
        .order_by(Task.created_at.desc())
        .all()
    )
    return render_template(
        "index.html",
        incomplete_tasks=incomplete_tasks,
        completed_tasks=completed_tasks,
        deleted_tasks=deleted_tasks,
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_task():
    if request.method == "POST":
        # フォームからデータを取得
        title = request.form["title"]
        description = request.form["description"]

        # 新しいタスクを作成
        new_task = Task(title=title, description=description, author=current_user)

        # データベースに追加して保存
        db.session.add(new_task)
        db.session.commit()
        flash("タスクが追加されました!")

        # タスク一覧ベージにリダイレクト
        return redirect(url_for("index"))

    # GETリクエストの場合、タスク追加フォームを表示
    return render_template("add_task.html")


@app.route("/complete/<int:id>")
@login_required
def complete_task(id):
    # 指定されたタスクのIDを取得
    task = Task.query.get_or_404(id)
    if task.author != current_user:
        flash("このタスクを編集する権限がありません。")
        return redirect(url_for("index"))

    # タスクの完了状態を切り替え
    task.completed = not task.completed

    # 変更を保存
    db.session.commit()

    # タスク一覧ページにリダイレクト
    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.author != current_user:
        flash("このタスクを削除する権限がありません。")
        return redirect(url_for("index"))
    task.is_deleted = True
    db.session.commit()
    flash("タスクが削除されました。")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user is None or not user.check_password(request.form["password"]):
            flash("無効なユーザー名またはパスワードです")
            return redirect(url_for("login"))
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        user = User(username=request.form["username"], email=request.form["email"])
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()
        flash("登録が完了しました!")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/deleted_tasks")
@login_required
def deleted_tasks():
    tasks = (
        Task.query.filter_by(author=current_user, is_deleted=True)
        .order_by(Task.created_at.desc())
        .all()
    )
    return render_template("deleted_tasks.html", tasks=tasks)


@app.route("/restore/<int:id>")
@login_required
def restore_task(id):
    task = Task.query.get_or_404(id)
    if task.author != current_user:
        flash("このタスクを復元する権限がありません。")
        return redirect(url_for("deleted_tasks"))
    task.is_deleted = False
    db.session.commit()
    flash("タスクが追加されました。")
    return redirect(url_for("deleted_tasks"))
