from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

from cloudipsp import Api, Checkout

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)
    # text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.title


@app.route('/')
def index():
    items = Item.query.order_by(Item.price.desc()).all()
    return render_template("index.html", data=items)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/buy/<int:id>')
def buy(id):
    try:
        item = Item.query.get(id)
        api = Api(merchant_id=1396424,
                  secret_key='test')
        checkout = Checkout(api=api)
        data = {
            "currency": "RUB",
            "amount": item.price * 100
        }
        url = checkout.url(data).get('checkout_url')
        return redirect(url)
    except:
        flash('Что-то пошло не так')
        return redirect('/')


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']
        item = Item(title=title, price=price)
        try:
            if title == "" or price == "":
                flash('Поля не могут быть пустыми')
                return render_template("create.html", mode='create')
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            flash('Не удалось создать товар')
            return render_template("create.html", mode='create')
    else:
        return render_template("create.html", mode='create')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == "GET":
        item = Item.query.filter_by(id=id).first()
        return render_template("create.html", mode='edit', item=item)
    else:
        title = request.form['title']
        price = request.form['price']
        item = Item.query.filter_by(id=id).first()
        try:
            if title == "" or price == "":
                flash('Поля не могут быть пустыми')
                return render_template("create.html", mode='edit', item=item)
            item.title = title
            item.price = price
            db.session.commit()
            return redirect('/')
        except:
            flash('Не удалось создать товар')
            return render_template("create.html", mode='edit', item=item)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    if request.method == "GET":
        item = Item.query.filter_by(id=id).first()
        try:
            db.session.delete(item)
            db.session.commit()
            return redirect('/')
        except:
            flash("Товар не найден")
            return redirect('/')
    else:
        return redirect('/')


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
