from flask import Flask,render_template,redirect,request
from flask.helpers import flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,current_user,LoginManager,AnonymousUserMixin
from flask import Flask, render_template, request, redirect, session, g, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)


class User(db.Model,UserMixin):
     id = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String(80), unique=True)
     email = db.Column(db.String(120), unique=True)
     password = db.Column(db.String(60))
     # posts = db.relationship('POST',backref='user',passive_deletes =True )
     # datecreated = db.Column(db.Datetime(timezone=True),default = func.now()
db.create_all()
db.session.commit()

@app.route('/', methods=['GET','POST'])
def login():
     if request.method == 'POST':
          email = request.form.get('email')
          password = request.form.get('password')
          correctemail = User.query.filter_by(email=email).first()
          # correctpassword = User.query.filter_by(password = password).first()
          if correctemail:
               if User.query.filter_by(password=password).first():
                    flash('logged in')
                    return redirect('/post')
               else:
                    flash('wrong password')
     return render_template('login.html')

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(id):
     return User.query.get(int(id))
@app.route('/home')
def home():
     return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def regist():
     if request.method == 'POST':
          email = request.form.get('email')
          username = request.form.get('name')
          password = request.form.get('password')
          password1 = request.form.get('password1')
          emailexist = User.query.filter_by(email = email).first()
          usernameexist = User.query.filter_by(username=username).first()
          print(usernameexist)
          if emailexist:
               flash('email already exist',category='error')
          elif usernameexist:
               flash('username already exist',category='error') 
          elif password != password1:
              flash('password don\'t mtach', category='error')
          else:
               signin = User(username=username, email=email, password=password)
               db.session.add(signin)
               db.session.commit()
               render_template('post.html',user = username)
               flash(f'user created with username{username}')
          class Anonymous(AnonymousUserMixin):
                    def __init__(self):
                         self.username = username
          login_manager.anonymous_user = Anonymous
          return redirect('/post')
          
     return render_template('signin.html')


def load_users():
    if current_user.is_authenticated():
        g.user = current_user.get_id() 
    else:
        g.user = None


class BlogPost(db.Model,UserMixin):
     id = db.Column(db.Integer, primary_key=True)
     content = db.Column(db.Text)
     dat_time = db.Column(db.DateTime, default=datetime.utcnow)

db.create_all()
db.session.commit()


@app.route("/post", methods=['GET', 'POST'])
def posts():
    if request.method == 'POST':
        post_content = request.form['content']
        new_post = BlogPost(content=post_content)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/post')
    else:
        all_posts = BlogPost.query.order_by(BlogPost.dat_time).all()
        username = request.form.get('name')
        render_template('signin.html')
        print(username)
        posts = BlogPost.query.all()
        user = User.query.filter_by(password=current_user).all()
        print(user)
        return render_template("post.html",posts = all_posts)



@app.route("/post/delete/<int:id>")
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/post')


@app.route("/post/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    post = BlogPost.query.get_or_404(id)

    if request.method == 'POST':
        post.content = request.form['content']
        db.session.commit()
        return redirect('/post')
    else:
        return render_template('edit.html', post=post)
if __name__ == '__main__':
     app.run(debug=False)
    
