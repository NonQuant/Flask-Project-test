from flask_restful import Resource
from flask import abort, jsonify
from . import db_session
from .jobs import Jobs
from .users import User
from .job_parser import parser
from datetime import datetime


def abort_if_job_not_found(job_id):
    session = db_session.create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, f"Job {job_id} not found")


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({'job': job.to_dict(
            only=("id", "team_leader", "job", "work_size",
                                       "collaborators", "start_date", "end_date", "is_finished"))})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        jobs = session.query(Jobs).all()
        return jsonify({'jobs': [job.to_dict(only=("id", "team_leader", "job", "work_size",
                                       "collaborators", "start_date", "end_date", "is_finished")) for job in jobs]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        job = Jobs(
            team_leader=args['team_leader'],
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args["collaborators"],
            is_finished=args['is_finished']
        )
        if args.get("start_date"):
            job.start_date = args["start_date"]
        else:
            job.start_date = datetime.now()

        if args.get("end_date"):
            job.end_date = args["end_date"]
        
        teamlead = session.query(User).filter(User.id == args["team_leader"]).first()
        if not teamlead:
            abort(404, f"Team leader {args['team_leader']} not found")
        teamlead.jobs.append(job)
        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})