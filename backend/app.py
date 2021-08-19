import os

import psycopg2
from flask import Flask, request
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.dispatcher import DispatcherMiddleware

DATABASE_URL = os.environ.get("DATABASE_URL")
SCHEMA_NAME = os.environ.get("SCHEMA_NAME", "public")
conn = psycopg2.connect(DATABASE_URL, options=f"-c search_path={SCHEMA_NAME}")

root = Flask(__name__)


@root.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e
    return str(e), 500


@root.route("/")
def entry():
    return "OK"


def query_db(query, args=(), one=False):
    with conn:
        with conn.cursor() as curs:
            curs.execute(query, args)
            r = [
                dict((curs.description[i][0], value) for i, value in enumerate(row))
                for row in curs.fetchall()
            ]
            return (r[0] if r else None) if one else r


@root.route("/doctor", methods=["POST"])
def create_doctor():
    doctor = request.get_json()
    return query_db(
        "INSERT INTO doctor (name, email, tags) VALUES (%s, %s, %s) RETURNING id",
        (doctor["name"], doctor["email"], doctor["tags"]),
        one=True,
    )


@root.route("/doctor/<string:doctor_id>", methods=["GET"])
def get_doctor(doctor_id):
    return query_db("SELECT * FROM doctor WHERE id = %s", (doctor_id,), one=True)


@root.route("/post", methods=["POST"])
def create_post():
    post = request.get_json()
    return query_db(
        "INSERT INTO post (owner, tags, content) VALUES (%s, %s, %s) RETURNING id",
        (post["owner"], post["tags"], post["content"]),
        one=True,
    )


@root.route("/post", methods=["PUT"])
def reply_post():
    reply = request.get_json()
    reply_id = query_db(
        "INSERT INTO post (owner, tags, content) VALUES (%s, %s, %s) RETURNING id",
        (reply["owner"], "{}", reply["content"]),
        one=True,
    )
    query_db(
        "UPDATE post SET replied = array_append(replied, %s) WHERE id = %s RETURNING id",
        (reply_id["id"], reply["post"]),
        one=True,
    )
    return reply_id


@root.route("/post/<string:post_id>", methods=["GET"])
def get_post(post_id):
    return query_db(
        "SELECT * FROM post WHERE id = %s",
        (post_id,),
        one=True,
    )


@root.route("/attachment", methods=["POST"])
def create_attachment():
    pass


app = DispatcherMiddleware(root)
