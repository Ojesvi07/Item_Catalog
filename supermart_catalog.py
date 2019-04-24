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
    items = session.query(SuperMart).all()
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

@app.route('/supermart/<int:supermart_category_id>/deletecategory',methods=['GET','POST'])
def DeleteCategory(supermart_category_id):
    deleteCategory=session.query(SuperMart).filter_by(id=supermart_category_id).one()
    if request.method == 'POST':
        session.delete(deleteCategory)
        session.commit()
        return redirect(url_for('SuperMartCategories'))
    else:
        return render_template('deletecategory.html',supermart_category_id=supermart_category_id,x=deleteCategory)


@app.route('/supermart/<int:supermart_category_id>/')
def ShowCategory(supermart_category_id):
    supermart = session.query(SuperMart).filter_by(
        id=supermart_category_id).one()
    items = session.query(Categories).filter_by(
        supermart_category_id=supermart_category_id)
    return render_template('newcategory.html', supermart_category_id=supermart_category_id, items=items, x=supermart)


@app.route('/supermart/<int:supermart_category_id>/additems/', methods=['GET', 'POST'])
def AddNewItem(supermart_category_id):
    if request.method == 'POST':
        newCategoryItem = Categories(name=request.form['name'], description=request.form['description'],
                                     price=request.form['price'], offer=request.form['offer'], supermart_category_id=supermart_category_id)
        session.add(newCategoryItem)
        session.commit()
        return redirect(url_for('ShowCategory', supermart_category_id=supermart_category_id))
    else:
        return render_template('newitem.html', supermart_category_id=supermart_category_id)

@app.route('/supermart/<int:supermart_category_id>/<int:category_id>/edititem', methods=['GET' ,'POST'])
def EditItem(supermart_category_id, category_id):
        editCategoryItem=session.query(Categories).filter_by(supermart_category_id=supermart_category_id,id=category_id).one()
        if request.method== 'POST':
            if request.form['name']:
                editCategoryItem.name=request.form['name']
            if request.form['description']:
                editCategoryItem.description=request.form['description']
            if request.form['price']:
                editCategoryItem.price=request.form['price']
            if request.form['offer']:
                editCategoryItem.offer=request.form['offer']
            session.add(editCategoryItem)
            session.commit()
            return redirect(url_for('ShowCategory',supermart_category_id=supermart_category_id))
        else:
            return render_template('edititem.html',supermart_category_id=supermart_category_id,category_id=category_id, x=editCategoryItem)    
    


@app.route('/supermart/<int:supermart_category_id>/<int:category_id>/deleteitem', methods=['GET', 'POST'])
def DeleteItem(supermart_category_id, category_id):
    deleteItem = session.query(Categories).filter_by(
        supermart_category_id=supermart_category_id, id=category_id).one()
    if request.method == 'GET':
        return render_template('deleteitem.html', supermart_category_id=supermart_category_id, category_id=category_id, x=deleteItem)
    if request.method== 'POST':
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('ShowCategory',supermart_category_id=supermart_category_id))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
