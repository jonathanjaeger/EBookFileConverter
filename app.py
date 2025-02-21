import os
import subprocess
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "converted"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        target_format = request.form["format"]

        if uploaded_file:
            input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            output_filename = os.path.splitext(uploaded_file.filename)[0] + "." + target_format
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            uploaded_file.save(input_path)

            command = f'ebook-convert "{input_path}" "{output_path}"'
            subprocess.run(command, shell=True, check=True)

            return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
