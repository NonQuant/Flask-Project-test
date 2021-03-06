import datetime
import flask_login
from flask import Flask, render_template, redirect, request, abort
from data import db_session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from data.departments import Department
from data.jobs import Jobs
from forms.departments import DepartmentsForm
from forms.login import LoginForm
from data.users import User
from forms.jobs import JobsForm
from forms.user import RegisterForm
from data import jobs_api, users_api
from requests import get
from flask_restful import Api
from data import users_resources, jobs_resources
import sqlalchemy_serializer



app = Flask(__name__)
api = Api(app)
api.add_resource(users_resources.UsersResource, "/api/v2/users/<int:user_id>")
api.add_resource(users_resources.UsersListResource, "/api/v2/users")
api.add_resource(jobs_resources.JobsResource, "/api/v2/jobs/<int:job_id>")
api.add_resource(jobs_resources.JobsListResource, "/api/v2/jobs")
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(users_api.blueprint)
    app.run()


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    workers_list = db_sess.query(User).all()
    workers_dict = {i.id: f"{i.surname} {i.name}" for i in workers_list}
    if current_user.is_authenticated:
        if current_user.id == 1:
            to_edit = [i.id for i in jobs]
        else:
            to_edit = [i.id for i in db_sess.query(Jobs).filter(Jobs.user == current_user).all()]
    else:
        to_edit = []
    return render_template("index.html", title="Main page", current_user=current_user, jobs=jobs, worker_dict=workers_dict, to_edit=to_edit)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='??????????????????????',
                                   form=form,
                                   message="???????????? ???? ??????????????????", current_user=flask_login.current_user)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='??????????????????????',
                                   form=form,
                                   message="?????????? ???????????????????????? ?????? ????????", current_user=flask_login.current_user)
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            city_from=form.city_from.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='??????????????????????', form=form, current_user=flask_login.current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user: User = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/index")
        return render_template('login.html',
                               message="???????????????????????? ?????????? ?????? ????????????",
                               form=form, current_user=current_user)
    return render_template("login.html", title="??????????????????????", form=form, current_user=current_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/addjob", methods=["GET", "POST"])
def add_job():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        teamlead: User = db_sess.query(User).filter(User.id == form.team_leader.data).first()
        if not teamlead:
            return render_template("job.html", title="Adding a job", current_user=current_user,
                           form=form, message="Teamlead not found")
        teamlead.jobs.append(job)
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.collaborators = form.collaborators.data
        job.start_date = datetime.datetime.now()
        job.is_finished = form.is_finished.data
        db_sess.commit()
        return redirect("/")
    return render_template("job.html", title="Adding a job", current_user=current_user,
                           form=form)


@app.route("/editjob/<int:id>", methods=["GET", "POST"])
@login_required
def edit_job(id):
    form = JobsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.id == 1:
            jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
        else:
            jobs: Jobs = db_sess.query(Jobs).filter(Jobs.id == id, Jobs.user == current_user).first()
        
        if jobs:
            form.team_leader.data = jobs.team_leader
            form.job.data = jobs.job
            form.work_size.data = jobs.work_size
            form.collaborators.data = jobs.collaborators
            form.is_finished.data = jobs.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.id == 1:
            jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
        else:
            jobs: Jobs = db_sess.query(Jobs).filter(Jobs.id == id, Jobs.user == current_user).first()

        if jobs:
            jobs.team_leader = form.team_leader.data
            jobs.job = form.job.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect("/")
        abort(404)
    return render_template("job.html", title="Editing a job", current_user=current_user,
                           form=form)


@app.route("/deletejob/<int:id>", methods=["GET", "POST"])
@login_required
def delete_jobs(id):
    db_sess = db_session.create_session()
    if current_user.id == 1:
        jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
    else:
        jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                          Jobs.user == current_user
                                          ).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/departments")
def departments():
    db_sess = db_session.create_session()
    deps = db_sess.query(Department).all()
    worker_list = db_sess.query(User).all()
    workers_dict = {i.id: f"{i.surname} {i.name}" for i in worker_list}
    if current_user.is_authenticated:
        if current_user.id == 1:
            to_edit = [i.id for i in deps]
        else:
            to_edit = [i.id for i in db_sess.query(Department).filter(Department.user == current_user).all()]
    else:
        to_edit = []
    return render_template("show_dep.html", title="List of Departments", current_user=current_user, deps=deps, worker_dict=workers_dict, to_edit=to_edit)


@app.route("/adddepartment", methods=["GET", "POST"])
def add_department():
    form = DepartmentsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        dep = Department(title=form.title.data,
                         members=form.members.data,
                         email=form.email.data)
        user = db_sess.query(User).filter(User.id == form.chief.data).first()
        if not user:
            return render_template("add_dep.html", title="Add Department", current_user=current_user, form=form, message="Chief not found!")
        user.departments.append(dep)
        db_sess.commit()
        return redirect("/departments")
    return render_template("add_dep.html", title="Add Department", current_user=current_user, form=form)

@app.route("/deletedepartment/<int:id>")
def delete_department(id):
    db_sess = db_session.create_session()
    if current_user.id == 1:
        dep = db_sess.query(Department).filter(Department.id == id).first()
    else:
        dep = db_sess.query(Department).filter(Department.id == id,
                                                Department.user == current_user
                                                ).first()
    if dep:
        db_sess.delete(dep)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departments')

@app.route("/editdepartment/<int:id>", methods=["GET", "POST"])
@login_required
def edit_department(id):
    form = DepartmentsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.id == 1:
            dep = db_sess.query(Department).filter(Department.id == id).first()
        else:
            dep = db_sess.query(Department).filter(Department.id == id,
                                                    Department.user == current_user
                                                    ).first()
        
        if dep:
            form.chief.data = dep.chief
            form.title.data = dep.title
            form.members.data = dep.members
            form.email.data = dep.email
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.id == 1:
            dep = db_sess.query(Department).filter(Department.id == id).first()
        else:
            dep = db_sess.query(Department).filter(Department.id == id,
                                                    Department.user == current_user
                                                    ).first()

        if dep:
            dep.chief = form.chief.data
            dep.title = form.title.data
            dep.members = form.members.data
            dep.email = form.email.data
            db_sess.commit()
            return redirect("/departments")
        abort(404)
    return render_template("add_dep.html", title="Editing a department", current_user=current_user,
                           form=form)


@app.route("/users_show/<int:user_id>")
def users_show(user_id):
    user_data = get(f"http://localhost:5000/api/users/{user_id}").json()
    if user_data.get("error"):
        abort(404)
    city: str = user_data["users"]["city_from"]
    city = city.replace(" ", "+")
    geocoder_request = f"https://geocode-maps.yandex.ru/1.x?geocode={city}&kind=locality&apikey=40d1649f-0493-4b70-98ba-98533de7710b&format=json"
    response = get(geocoder_request)

    if response:
        json = response.json()
        toponym = json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        coors: str = toponym["Point"]["pos"].replace(" ", ",")
    map_request = f"http://static-maps.yandex.ru/1.x/?ll={coors}&spn=0.08,0.08&l=sat"
    response = get(map_request)
    img = "./static/hometown.png"
    with open(img, "wb") as file:
        file.write(response.content)
    name = user_data["users"]["name"] + " " + user_data["users"]["surname"]
    city_name = user_data["users"]["city_from"]
    return render_template("show_city.html", title="Hometown", current_user=current_user, name=name, city_name=city_name)


if __name__ == '__main__':
    main()
