from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import NumberRange, DataRequired
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.ext.hybrid import hybrid_property
from flask import request, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf

app = Flask(__name__)
csrf = CSRFProtect(app)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "ben should eat glass for dinner"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
db = SQLAlchemy(app)

class open_cafe(db.Model):
    __tablename__ = 'cafe_menu'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column (db.String(16), index = True, unique = True, nullable = False)
    price = db.Column (db.Float, nullable = False)
    description = db.Column(db.String)
    image  = db.Column(db.String)

#Maybe create a page that allows the user to buy the items and then displays all the pictures in a fun way to represent the items bought.It then resets the basket

# Want to create a basket for each user where user can add items and amount. Add constraints to the amount they can add, if item already exists then just increment the value there 
class basket(db.Model):
    __tablename__ = 'user_basket'
    id = db.Column(db.Integer, primary_key = True)
    item_id = db.Column (db.Integer, db.ForeignKey('cafe_menu.id')) 
    item_quantity = db.Column (db.Integer, nullable = False)
    item = db.relationship('open_cafe', backref = 'baskets')

    @hybrid_property
    def total_price(self):
        return self.item_quantity * self.item.price
# Want to create a login page, or a sign up page
# Each user has a unique id, name, password and basket_id
# Options to view the user account at all times, reset password?, delete account, try emailing for code?


class recipe (db.Model):
    __tablename__ = 'all_recipes'
    id = db.Column(db.Integer, primary_key = True)
    item_id = db.Column (db.Integer, db.ForeignKey('cafe_menu.id'))
    ingredients = db.relationship('ingredient_recipe_amount', back_populates = 'recipe')

    @hybrid_property
    def total_carbon_footprint(self):
        total = 0
        for ingredient_recipe in self.ingredients:
            total += ingredient_recipe.amount * ingredient_recipe.ingredient.carbon_footprint
        return total


class ingredients (db.Model):
    __tablename__ = 'all_ingredients'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique = True, nullable = False)
    carbon_footprint = db.Column (db.Integer)
    ingredient_recipe_amounts = db.relationship('ingredient_recipe_amount', back_populates='ingredient') 

class ingredient_recipe_amount(db.Model):
    __tablename__ = 'ingredients_for_each_recipe'
    id = db.Column (db.Integer, primary_key = True)
    recipe_id = db.Column(db.Integer, db.ForeignKey ('all_recipes.id'))
    ingredient_id = db.Column (db.Integer, db.ForeignKey ('all_ingredients.id'))
    amount = db.Column (db.Float)
    recipe = db.relationship('recipe', back_populates = 'ingredients')
    ingredient = db.relationship('ingredients', back_populates = 'ingredient_recipe_amounts')


"""
class user(db.Model):
    __tablename__ = 'User Information'
    id = db.Column (db.Integer, primary_key = True)
    name = db.Column (db.String(45), index = True, unique = True, nullable = False)
    password = db.Column (db.String(24), unique = True, nullable = False) # Make it so the password is hidden?
    basket_id = db.Column (db.Integer) # It is a foreign key, the parent key is a basket record. I want to create a new basket when a new user is created
class user_list (db.Model):
    __tablename__ = 'Users List'
    user_id = db.Column (db.Integer) # This is a foreign key, its parent is id from user
    purchase_amount = db.Column (db.Float) # Using the basket it calculates through the amount bought and price the total money spent by the user
"""

class Basket_form(FlaskForm):
    amount = IntegerField('Add the desired amount', validators = [DataRequired(), NumberRange(min = 1, max = 15)])
    buy = SubmitField('Buy')


@app.route('/')
def galleryPage():
    cafe_menu = open_cafe.query.all()
    cafe_recipes = recipe.query.all()
    csrf_token = generate_csrf()
    return render_template('index.html',cafe_menu = cafe_menu, cafe_recipes = cafe_recipes, csrf_token = csrf_token)


@app.route('/product_page/<int:item>', methods = ['GET', 'POST'])
def singleProductPage(item):
    purchase_form = Basket_form()
    selected_item = open_cafe.query.get_or_404(item)
    if purchase_form.validate_on_submit():
        print("Form validated! Processing basket...")
        quantity = purchase_form.amount.data
        item_entry = basket.query.filter_by(item_id = selected_item.id).first()

        if item_entry:
            item_entry.item_quantity += quantity
        else:
            item_entry = basket(item_id = selected_item.id, item_quantity = quantity)
            db.session.add(item_entry)
        db.session.commit()
        return render_template('PurchaseProduct.html', item=selected_item, quantity_added = quantity, basket_entry=item_entry) 
    else: 
        return render_template('SingleProduct.html', cafe_item = selected_item, basket = purchase_form)
    
# @app.route('user/basket')
@app.route('/basket')
def basketPage():
    user_basket = basket.query.all()
    return render_template('ViewBasket.html', user_basket = user_basket)

@app.route('/add_to_basket', methods = ['POST'])
def add_to_basket():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity')

    item_entry = basket.query.filter_by(item_id = item_id).first()

    if item_entry:
        item_entry.item_quantity += quantity
    else:
        item_entry = basket(item_id = item_id, item_quantity = quantity)
        db.session.add(item_entry)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/get_item_description', methods = ['POST'])
def get_item_description():
    data = request.get_json()
    item_id = data.get('item_id')
    item_entry = open_cafe.query.filter_by(id = item_id).first()

    if item_entry:
        return jsonify({"description" : item_entry.description})
    else:
        return jsonify({"error" : "Item not found"}), 404
    

if __name__ == '__main__':
    app.run(debug=True)


"""
Allows for calculation of total price in SQL
@total_price.expression
def total_price(cls):
    return cls.item_quantity * open_cafe.price
"""
"""{% extends "base.html" %}
<!DOCTYPE html>
<body>
   <h1> {{ item.name }}</h1>
   <h3>Items Added: </h3>
   <p> {{ basket_entry.item_quantity }} </p>
</body>"""