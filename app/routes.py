from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from app.models import User, Task
from werkzeug.urls import url_parse
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField("ユーザー名", validators=[DataRequired()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    submit = SubmitField("ログイン")


class RegistrationForm(FlaskForm):
    username = StringField("ユーザー名", validators=[DataRequired()])
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    password2 = PasswordField(
        "パスワード（確認）", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("登録")


class TaskForm(FlaskForm):
    title = StringField("タイトル", validators=[DataRequired()])
    description = TextAreaField("説明")
    submit = SubmitField("タスクを追加")


@app.route("/")
@login_required
def index():
    incomplete_tasks = (
        Task.query.filter_by(
            user_id=current_user.id, completed=False, is_archived=False
        )
        .order_by(Task.created_at.desc())
        .all()
    )
    completed_tasks = (
        Task.query.filter_by(user_id=current_user.id, completed=True, is_archived=False)
        .order_by(Task.created_at.desc())
        .all()
    )
    archived_tasks = (
        Task.query.filter_by(user_id=current_user.id, is_archived=True)
        .order_by(Task.created_at.desc())
        .all()
    )
    return render_template(
        "index.html",
        incomplete_tasks=incomplete_tasks,
        completed_tasks=completed_tasks,
        archived_tasks=archived_tasks,
    )


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            author=current_user,
        )
        db.session.add(new_task)
        db.session.commit()
        flash("タスクが追加されました!")
        return redirect(url_for("index"))
    return render_template("add_task.html", form=form)


@app.route("/complete/<int:id>")
@login_required
def complete_task(id):
    task = Task.query.get_or_404(id)
    if task.author != current_user:
        flash("このタスクを編集する権限がありません。")
        return redirect(url_for("index"))
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/archive/<int:id>")
@login_required
def archive_task(id):
    task = Task.query.get_or_404(id)
    if task.author != current_user:
        flash("このタスクをアーカイブする権限がありません。")
        return redirect(url_for("index"))
    task.is_archived = True
    db.session.commit()
    flash("タスクがアーカイブされました。")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("無効なユーザー名またはパスワードです")
            return redirect(url_for("login"))
        login_user(user)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("登録が完了しました!")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/archived_tasks")
@login_required
def archived_tasks():
    tasks = (
        Task.query.filter_by(author=current_user, is_archived=True)
        .order_by(Task.created_at.desc())
        .all()
    )
    return render_template("archived_tasks.html", tasks=tasks)


@app.route("/restore/<int:id>")
@login_required
def restore_task(id):
    task = Task.query.get_or_404(id)
    if task.author != current_user:
        flash("このタスクを復元する権限がありません。")
        return redirect(url_for("archived_tasks"))
    task.is_archived = False
    db.session.commit()
    flash("タスクが復元されました。")
    referer = request.headers.get("Referer")
    if referer:
        return redirect(referer)
    else:
        return redirect(url_for(index))


@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.author != current_user:
        flash("このタスクを削除する権限がありません。")
        return redirect(url_for("index"))
    db.session.delete(task)
    db.session.commit()
    flash("タスクを削除しました。")
    return redirect(url_for("index"))


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_task(id):
    task = Task.query.get_or_404(id)
    if task.author != current_user:
        flash("このタスクを編集する権限がありません。")
        return redirect(url_for("index"))

    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        db.session.commit()
        flash("タスクの内容が変更されました!")
        return redirect(url_for("index"))
    elif request.method == "GET":
        form.title.data = task.title
        form.description.data = task.description
    return render_template("edit_task.html", task=task, form=form)
