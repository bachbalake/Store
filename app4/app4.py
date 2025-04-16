from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange, DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "ben should eat glass for dinner"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
db = SQLAlchemy(app)

class open_cafe(db.Model):
    __tablename__ = 'Cafe Menu'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column (db.String(16), index = True, unique = True, nullable = False)
    price = db.Column (db.Float, nullable = False)
    description = db.Column(db.String)
    image  = db.Column(db.String)


class Basket_form(FlaskForm):
    amount = IntegerField('Add the desired amount', validators = [DataRequired(), NumberRange(min = 1, max = 15)])
    buy = SubmitField('Buy')

@app.route('/')
def galleryPage():
    cafe_menu = open_cafe.query.all()
    return render_template('index.html',cafe_menu = cafe_menu)


@app.route('/product_page/<int:item>', methods = ['GET', 'POST'])
def singleProductPage(item):
    purchase_form = Basket_form()
    selected_item = open_cafe.query.get_or_404(item)
    if purchase_form.validate_on_submit():
        return render_template('PurchaseProduct.html', cafe_item = selected_item, basket = purchase_form.amount.data)
    else: 
        return render_template('SingleProduct.html', cafe_item = selected_item, basket = purchase_form)

if __name__ == '__main__':
    app.run(debug=True)


