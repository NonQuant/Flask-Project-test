from datetime import datetime
import flask

from . import db_session
from .jobs import Jobs
from flask import jsonify, make_response, request
from .users import User

blueprint = flask.Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates'
)


@blueprint.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


@blueprint.route('/api/jobs')
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {
            "jobs": [job.to_dict(only=("id", "team_leader", "job", "work_size",
                                       "collaborators", "start_date", "end_date", "is_finished")) for job in jobs]
        }
    )

@blueprint.route("/api/jobs/<int:job_id>")
def get_one_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == job_id).first()
    if not job:
        return jsonify(
            {
                "error": "Not found"
            }
        )
    return jsonify(
        {
            "jobs": job.to_dict(only=("id", "team_leader", "job", "work_size",
                                       "collaborators", "start_date", "end_date", "is_finished"))
        }
    )

@blueprint.route("/api/jobs", methods=["POST"])
def create_jobs():
    if not request.json:
        return jsonify({"error": "Empty request"})
    elif not all(key in request.json for key in 
                 ["team_leader", "job", "work_size",
                  "collaborators", "is_finished"]):
        return jsonify({"error": "Bad request"})
    db_sess = db_session.create_session()
    
    if request.json.get("id"):
        possible_job = db_sess.query(Jobs).filter(Jobs.id == request.json.get("id")).first()
        if possible_job:
            return jsonify({"error": "Id already exists"})
        jobs = Jobs(id=request.json.get("id"))
    else:
        jobs = Jobs()

    jobs.job = request.json["job"]
    jobs.work_size = request.json["work_size"]
    jobs.collaborators = request.json["collaborators"]
    jobs.is_finished = request.json["is_finished"]

    if request.json.get("start_date"):
        jobs.start_date = request.json["start_date"]
    else:
        jobs.start_date = datetime.now()

    if request.json.get("end_date"):
        jobs.end_date = request.json["end_date"]

    teamlead = db_sess.query(User).filter(User.id == request.json["team_leader"]).first()
    if not teamlead:
        return jsonify({"error": "Bad request"})
    teamlead.jobs.append(jobs)
    db_sess.add(jobs)
    db_sess.commit()
    return jsonify({"success": "OK"})

@blueprint.route("/api/jobs/<int:jobs_id>", methods=["DELETE"])
def delete_jobs(jobs_id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == jobs_id).first()
    if not jobs:
        return jsonify({"error": "Not found"})
    db_sess.delete(jobs)
    db_sess.commit()
    return jsonify({"success": "OK"})


@blueprint.route("/api/jobs/<int:jobs_id>", methods=["PUT"])
def edit_jobs(jobs_id):
    data = request.json
    if not data:
        return jsonify({"error": "Empty request"})
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).filter(Jobs.id == jobs_id).first()
    if not job:
        return jsonify({"error": "Not found"})
    for i in data.keys():
        if i not in ("team_leader", "job", "work_size", "collaborators", "start_date", "end_date", "is_finished"):
            return jsonify({"error": "Bad request"})
        if i == "team_leader":
            job.team_leader = data[i]
        if i == "job":
            job.job = data[i]
        if i == "work_size":
            job.work_size = data[i]
        if i == "collaborators":
            job.collaborators = data[i]
        if i == "start_date":
            job.start_date = data[i]
        if i == "end_date":
            job.end_date = data[i]
        if i == "is_finished":
            job.is_finished = data[i]
    db_sess.commit()
    return jsonify({"success": "OK"})
