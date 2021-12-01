from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from forms import LoginForm, RegistrationForm, ForumPostForm, CommentForm
from models import User, Post, Comment, db, app


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    all_posts = Post.query.all()
    all_comments = Comment.query.all()

    post_form = ForumPostForm()
    comment_form = CommentForm()
    if post_form.validate_on_submit():
        post = Post(body=post_form.post.data)
        db.session.add(post)
        db.session.commit()
        flash('Succesfully posted!')
        return redirect('index')
    return render_template('index.html', title='Home', posts=all_posts, form=post_form, comment_form=comment_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Succesfully registered!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
