from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

#Создание самой страницы
app = Flask(__name__, template_folder="template", static_folder="static",)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
database = SQLAlchemy(app) #Создание таблицы данных
locked_flag = True  #Переменная, проверяющая зашел ли пользователь или нет

#Создание профилей для ввода в таблицу
class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(100), unique = True)
    password = database.Column(database.String(100), nullable = True)
    date = database.Column(database.DateTime, default=datetime.utcnow)  

    hook = database.relationship("Profiles", backref="users", uselist=False)

    def __repr__ (self):
        return f"<User {self.id}>" 
class Profiles (database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(100), nullable=True)
    old = database.Column(database.Integer)
    city = database.Column(database.String(100))

    user_id = database.Column(database.Integer, database.ForeignKey('users.id'))

    def __repr__(self):
        return f"<Profiles {self.id}>"


#Запуск и работа страницы "index.html"
@app.route("/")
def index():
    return render_template("index.html")

#Запуск и работа страницы "register.html"
@app.route("/register", methods = ["GET", "POST"]) #Методы для получения и регистрации данных в таблицу данных
def register():
    if request.method == "POST":
        try:
            user = Users(email=request.form["email"], password = request.form["password"])
            database.session.add(user)
            database.session.flush()

            profile = Profiles(name = request.form["name"], old = request.form["old"], city = request.form["city"], user_id = user.id)
            database.session.add(profile)
            database.session.commit()
        except:
            database.session.rollback()
            print("Ошибка в базе данных")    

    return render_template("register.html")

#Запуск и работа страницы "locked.html"
@app.route("/locked")
def locked():
    global locked_flag
    if locked_flag == False: #Проверка, зашел ли пользователь или нет
        return render_template('locked.html')
    else:
        return redirect("/register")

#Запуск и работа страницы "login.html"
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST": #Пользователь вводит данные и идет поиск этих данных по таблице данных
        user = Users.query.filter_by(email = request.form["email"], password = request.form["password"]).first()
        if user: #Если данные найдены, то меняем значение переменной locked_flag
            global locked_flag
            locked_flag = False
            return redirect("/locked")
    return render_template("login.html")


with app.app_context():
    database.create_all()

#Добавление страниц, адрес и функции
if __name__ == "__main__":
    app.add_url_rule("/", "index", index)
    app.add_url_rule("/register", "register", register)
    app.add_url_rule("/locked", "locked", locked)
    app.add_url_rule("/login", "login", login)
    app.run(debug = True)