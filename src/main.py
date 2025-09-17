from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/<qrid>", methods=['GET'])
def landing(qrid: int):
    return render_template("landing.html", qrid=qrid)


@app.route("/db/add", methods=['POST'])
def record_vote():
    try:
        qrid = request.form.get('qrid')
        taiwan = request.form.get('taiwan')
    except Exception as e:
        None

    return "thank you for your vote"




if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)