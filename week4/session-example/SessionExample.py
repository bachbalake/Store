from flask import Flask, render_template, request, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = "top secret password don't tell anyone this"

class CommentForm(FlaskForm):
    comment = StringField('Add comment: ',validators = [DataRequired()])
    submit = SubmitField('Submit')

@app.route('/',methods=['GET','POST'])
def main_page():
    # if there is no list of comments in session, create an empty list to store them
    if 'comments' not in session:
        print("New session",flush=True)
        session['comments'] = []
    
    # if form is submitted, add comment to session data
    form = CommentForm()
    if form.validate_on_submit():
        session['comments'] += [form.comment.data]
        
    return render_template('index.html',form=form,comments = session['comments'])

if __name__ == '__main__':
    app.run(debug=True,port=5050)
