from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

class Technology(db.Model):
    __tablename__ = 'technologies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), index=True, unique=True)
    taught = db.Column(db.String(32))
    description = db.Column(db.Text)
    
@app.route('/')
def index():
    techs = Technology.query.all()
    return render_template('index.html', technologies = techs)

if __name__ == '__main__':
    app.run(debug=True,port=5050)
