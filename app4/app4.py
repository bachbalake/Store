from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange, DataRequired
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "ben should eat glass for dinner"

cafe_menu = [
    { "name": "Ca Phe Muoi", "price": 5.35, "description": "A salted caramel Vietnamese drink made with a combination of Vietnamese coffee, condensed milk and just a little bit of salt", "image" : "ca phe muoi.jpg"},
    { "name": "Matcha Tonic", "price": 4.20, "description": "A refreshing drink with fruity tones and earthly matcha","image" : "matcha tonic.jpg" },
    { "name": "Irish Coffee", "price": 7.50, "description": "An uplifting caffeinated alcoholic drink made of Irish whiskey, coffee and sweetners.", "image" : "irish coffee.jpg" },
    { "name": "Affogato", "price": 4.75, "description": "A sweet treat made by pouring a shot of espresso over a scoop of vanilla ice cream", "image" : "affogato.jpg" }
]

class Basket_form(FlaskForm):
    amount = IntegerField('Add the desired amount', validators = [DataRequired(), NumberRange(min = 1, max = 15)])
    buy = SubmitField('Buy')

@app.route('/')
def galleryPage():
    return render_template('index.html',cafe_menu = cafe_menu)

@app.route('/product_page/<int:item>', methods = ['GET', 'POST'])
def singleProductPage(item):
    purchase_form = Basket_form()
    if purchase_form.validate_on_submit():
        return render_template('PurchaseProduct.html', cafe_item = cafe_menu[item], basket = purchase_form.amount.data)
    else: 
        return render_template('SingleProduct.html', cafe_item = cafe_menu[item], basket = purchase_form)

if __name__ == '__main__':
    app.run(debug=True)


