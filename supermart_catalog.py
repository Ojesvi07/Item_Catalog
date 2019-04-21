from flask import Flask, render_template, redirect, url_for, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, SuperMart, Categories
app = Flask(__name__)


engine = create_engine('sqlite:///supermart.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


@app.route('/')
@app.route('/supermart/')
def SuperMartCategories():
    items = session.query(Categories).all()
    return render_template('supermartcategory.html', items=items)


@app.route('/supermart/addcategory/', methods=['GET', 'POST'])
def AddCategory():

    if request.method == 'POST':
        newCategory = SuperMart(category=request.form['category'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('SuperMartCategories'))
    else:
        return render_template('addcategory.html')




if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
