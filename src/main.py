import sqlite3

from flask import Flask, render_template, request
from dbhandler import add_vote_record, add_loc_record

app = Flask(__name__)

@app.route("/<int:qr_id>", methods=['GET', 'POST'])
def landing(qr_id: int):
    """
    Handles servicing the landing page.
    :param qr_id: qr code id distinguishing specific group of qr codes
    :return:
    """
    if request.method == 'POST':
        add_vote_record(db, request.form)

    print(qr_id, request.method)

    return render_template('landing.html', qr_id=qr_id)


@app.route("/setqrloc", methods=['GET', 'POST'])
def set_qr_loc():
    if request.method == 'POST':
        add_loc_record(db, request.form)

    return render_template('set_qr_loc.html')



if __name__ == '__main__':
    db = sqlite3.connect("../myfuckingdb.db")
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS qr2loc (id INTEGER PRIMARY KEY, lat FLOAT, lng FLOAT);")
    cur.execute("CREATE TABLE IF NOT EXISTS response2qr (id INTEGER PRIMARY KEY, response TEXT, qrid INTEGER);")

    app.run(host="127.0.0.1", port=8000, debug=True)