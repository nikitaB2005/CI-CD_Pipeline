from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route("/")
def dashboard():
    with open("build_info.json", "r") as file:
        build_info = json.load(file)

    return render_template("index.html", build=build_info)

@app.route("/api/build-info")
def api():

    with open("build_info.json") as f:
        return json.load(f)

@app.route("/health")
def health():

    return {

        "status":"UP"

    }

if __name__ == "__main__":
    app.run(debug=True)