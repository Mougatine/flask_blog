from sqlalchemy import desc
from flask import render_template, flash, redirect
from flask_login import login_user, logout_user, login_required, current_user
from mistune import Markdown, Renderer

from app import app, login_manager, db
from .forms import LoginForm, SignupForm, WriterForm, ChangePasswordForm
from .models import User, Post

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
@app.route('/index')
def index():  # TODO: Should be different from rest of the blg
    """Main page"""
    return redirect('/blog')


#@app.before_first_request
def fill_posts():
    db.drop_all()
    db.create_all()
    db.session.add(User(username='admin', password='password'))
    for i in range(30, 0, -1):
        db.session.add(Post(title='test' + str(i),
                            intro='intro blablabla sera plus long...',
                            content='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'))
    db.session.commit()


@app.route('/blog')
def blog():
    """Main page of the blog, list all articles."""
    posts = Post.query.order_by(desc(Post.date)).limit(10)

    return render_template('blog.html',
                           title='Blog',
                           posts=posts,
                           next_page=2)


@app.route('/blog/page/<int:page_number>')
def blog_next_pages(page_number):
    """Older pages of the blog"""
    post_number = 10
    current_index = (post_number + 1) * (page_number - 1) - 1
    posts = Post.query.order_by(desc(Post.date)).all()

    if len(posts) <= current_index + 11:  # We have reached the end of the post
        next_page = None
    else:
        next_page = page_number + 1

    posts = posts[current_index:current_index + 11]

    return render_template('blog.html',
                           title='Blog',
                           posts=posts,
                           next_page=next_page)

@app.route('/blog/<string:title>')
def article(title):
    post = Post.get_post(title)

    markdown = Markdown()
    return render_template('article.html',
                           post=post,
                           markdown=markdown)
# ----------------------------------------------------------------------------
# Admin
# ----------------------------------------------------------------------------


@app.route('/change_password')
@login_required
def change_password():
    """Admin panel for changing password"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if User.test_passwords(current_user.password, form.old_pwd.data):
            if form.new_pwd.data == form.confirm_pwd.data:
                user.set_password(form.new_pwd.data)
                db.session.commit()
                return redirect('/blog')
            else:
                flash("The new password does not match the confirmation")
        else:
            flash("The 'old' password is incorrect")
    return render_template('change_password.html',
                            title='Change your password',
                            form=form)


@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    form = WriterForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    intro=form.intro.data,
                    content=form.content.data)
        db.session.add(post)
        db.session.commit()
        return redirect('/blog')
    return render_template('writer.html',
                           form=form,
                           form_style='width: 100%;'
                                      'background-color: whitesmoke;'
                                      'border: 5px solid darkgrey')

# ----------------------------------------------------------------------------
# Session
# ----------------------------------------------------------------------------


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page. Only accessible by modifying the url."""
    form = LoginForm()

    if form.validate_on_submit():
        user = User.get_user(form.username.data, form.password.data)
        if user:
            db.session.add(user)
            db.session.commit()

            login_user(user)

            return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """User creation page"""
    form = SignupForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        user.is_authenticated = False
        db.session.add(user)
        db.session.commit()
        logout_user()

        return redirect('/index')
    return render_template('register.html',
                           title='Sign Up',
                           form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Logout page"""
    user = current_user

    user.is_authenticated = False
    db.session.add(user)
    db.session.commit()

    logout_user()
    return redirect('/index')

# ----------------------------------------------------------------------------
# Error handlers
# ----------------------------------------------------------------------------


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
