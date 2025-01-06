from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

# إنشاء تطبيق Flask
app = Flask(__name__)

# تكوين قاعدة البيانات (SQLite في هذه الحالة)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إنشاء قاعدة البيانات
db = SQLAlchemy(app)

# نموذج بيانات لتخزين المعلومات في قاعدة البيانات
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.content}')"

# قبل كل طلب لتحديث أو إنشاء قاعدة البيانات إذا لم تكن موجودة
@app.before_request
def before_request():
    db.create_all()

# الصفحة الرئيسية التي تعرض جميع المنشورات
@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

# صفحة لإضافة منشور جديد
@app.route('/add', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')
    return render_template('add_post.html')

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)
