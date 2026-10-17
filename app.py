import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from log_analyzer import analyze_logs

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"log", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def home():
    results = None
    error = None

    if request.method == "POST":
        uploaded_file = request.files.get("logfile")

        if not uploaded_file or uploaded_file.filename == "":
            error = "Please select a log file."

        elif not allowed_file(uploaded_file.filename):
            error = "Only .log and .txt files are allowed."

        else:
            filename = secure_filename(uploaded_file.filename)

            if not filename:
                error = "Invalid filename."
            else:
                filepath = os.path.join(
                    app.config["UPLOAD_FOLDER"], filename
                )

                try:
                    uploaded_file.save(filepath)
                    results = analyze_logs(filepath)

                except OSError:
                    error = "Unable to read the uploaded file."

                finally:
                    if os.path.exists(filepath):
                        os.remove(filepath)

    return render_template(
        "index.html",
        results=results,
        error=error
    )


@app.errorhandler(413)
def file_too_large(error):
    return "File is too large. Please upload a file under 5 MB.", 413
if __name__ == "__main__":
    app.run(debug=True, port=8000)