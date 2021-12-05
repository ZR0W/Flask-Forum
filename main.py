from flask import render_template, flash, redirect, url_for, request
from flask_mail import Mail, Message
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from forms import LoginForm, RegistrationForm, ForumPostForm, CommentForm
from models import User, Post, Comment, db, app

email_addr = "flaskforumcsc210@gmail.com"
app.config['MAIL_SERVER']= "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = email_addr
app.config['MAIL_PASSWORD'] = "fall21flask@abcxyz#"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def get_user():
    user_info = User.query.all()
    all_users = {}
    for user in user_info:
        all_users[user.id] = [user.username, user.email]
    return all_users


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    query = User.query
    all_posts = Post.query.all()
    all_users = get_user()
    all_comments = Comment.query.all()
    post_form = ForumPostForm()
    comment_form = CommentForm()
    if post_form.validate_on_submit():
        post = Post(title=post_form.title.data, body=post_form.body.data, user_id=current_user.get_id())
        db.session.add(post)
        db.session.commit()
        try: 
            msg = Message("New Post Created!", sender = email_addr, recipients = [email_addr, all_users[int(current_user.get_id())][1]])
            msg.body = "Hi " + all_users[int(current_user.get_id())][0] + "!\n\nA new discussion thread has been created by YOU! Stay tuned!\n\n - FF"
            mail.send(msg)
        except:
            print("Unable to send email")
        return redirect(url_for('index', _anchor="end"))
    return render_template('index.html', title='Home', posts=all_posts, users=all_users, query=query,
                        comments=all_comments, form=post_form, comment_form=comment_form)


@app.route('/upvote/<post_id>', methods=['GET', 'POST'])
@login_required
def upvote_post(post_id):
    db.session.query(Post).filter(Post.id == post_id).update({"upvotes": (Post.upvotes + 1)})
    db.session.commit()
    return redirect(url_for('index', _anchor="post_"+post_id))


@app.route('/downvote/<post_id>', methods=['GET', 'POST'])
@login_required
def downvote_post(post_id):
    db.session.query(Post).filter(Post.id == post_id).update({"downvotes": (Post.downvotes - 1)})
    db.session.commit()
    return redirect(url_for('index', _anchor="post_"+post_id))


@app.route('/post/edit/<post_id>', methods=['POST', 'GET'])
@login_required
def edit_post(post_id):
    post_form = ForumPostForm()
    post = db.session.query(Post).filter(Post.id == post_id).one()
    if request.method == 'GET':
        post_form.title.data = post.title
        post_form.body.data = post.body
    if request.method == 'POST' and post_form.validate_on_submit():
        post.title = post_form.title.data
        post.body = post_form.body.data
        db.session.commit()
        return redirect(url_for('index', _anchor="post_"+post_id))
    return render_template('edit_post.html', title='Edit', form=post_form)


@app.route('/post/delete/<post_id>', methods=['DELETE', 'GET'])
@login_required
def delete_post(post_id):
    db.session.query(Post).filter(Post.id == post_id).delete()
    db.session.query(Comment).filter(Comment.post_id == post_id).delete()
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/comment/<post_id>', methods=['POST'])
@login_required
def comment(post_id):
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        comment = Comment(body=comment_form.body.data, post_id=post_id, user_id=current_user.get_id())
        db.session.add(comment)
        db.session.commit()
    return redirect(url_for('index', _anchor="post_"+post_id))


@app.route('/comment/upvote/<comment_id>', methods=['GET', 'POST'])
@login_required
def upvote_cmt(comment_id):
    db.session.query(Comment).filter(Comment.id == comment_id).update({"upvotes": (Comment.upvotes + 1)})
    db.session.commit()
    return redirect(url_for('index', _anchor="cmt_"+comment_id))


@app.route('/comment/downvote/<comment_id>', methods=['GET', 'POST'])
@login_required
def downvote_cmt(comment_id):
    db.session.query(Comment).filter(Comment.id == comment_id).update({"downvotes": (Comment.downvotes - 1)})
    db.session.commit()
    return redirect(url_for('index', _anchor="cmt_"+comment_id))


@app.route('/comment/edit/<post_id>/<comment_id>', methods=['POST', 'GET'])
@login_required
def edit_cmt(comment_id, post_id):
    comment_form = CommentForm()
    comment = db.session.query(Comment).filter(Comment.id == comment_id).one()
    if request.method == 'GET':
        comment_form.body.data = comment.body
    if request.method == 'POST' and comment_form.validate_on_submit():
        comment.body = comment_form.body.data
        db.session.commit()
        return redirect(url_for('index', _anchor="cmt_"+comment_id))
    return render_template('edit_cmt.html', title='Edit', form=comment_form)


@app.route('/comment/delete/<post_id>/<comment_id>', methods=['DELETE', 'GET'])
@login_required
def delete_cmt(post_id, comment_id):
    db.session.query(Comment).filter(Comment.id == comment_id).delete()
    db.session.commit()
    return redirect(url_for('index', _anchor="post_"+post_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
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
        flash('Successfully registered!')
        try:
            msg = Message("Welcome to Flask Forum!", sender = email_addr, recipients = [email_addr, form.email.data])
            msg.body = "Hi " + form.username.data + "!\n\nThank you for registering! Hope you enjoy the ride :)\n\n- FF"
            mail.send(msg)
        except:
            print("Unable to send email")
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)