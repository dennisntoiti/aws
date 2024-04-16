import boto3
import uuid

from flask import Flask, redirect, url_for, request, render_template
from flask_sqlalchemy import SQLAlchemy

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(100))
    filename = db.Column(db.String(100))
    bucket = db.Column(db.String(100))
    region = db.Column(db.String(100))

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

    db.init_app(app)

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            uploaded_file = request.files["file-to-save"]
            if not allowed_file(uploaded_file.filename):
                return "FILE NOT ALLOWED!"

            new_filename = uuid.uuid4().hex + '.' + uploaded_file.filename.rsplit('.', 1)[1].lower()

            bucket_name = "dennisvividstudio"
            s3 = boto3.resource(
                service_name = 's3',
                region_name = 'eu-north-1',
                aws_access_key_id = 'AKIATLR4YZYWD2COI7UA',
                aws_secret_access_key = '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'
            )
            s3.Bucket(bucket_name).upload_fileobj(uploaded_file, new_filename)

            file = File(original_filename=uploaded_file.filename, filename=new_filename,
                bucket=bucket_name, region="us-east-2")

            db.session.add(file)
            db.session.commit()

            # Redirect to the /upload page after form submission
            return redirect(url_for("upload"))

        files = File.query.all()

        return render_template("index.html", files=files)

    @app.route("/upload")
    def upload():
        return render_template("upload.html")

    return app
