import base64
import sqlite3
from io import BytesIO

from flask import Flask, render_template, request, make_response
from flask import Flask, render_template, request
from qrcode.main import make

from dbhandler import add_vote_record, add_loc_record

app = Flask(__name__)

@app.route("/<int:qr_id>", methods=['GET', 'POST'])
def landing(qr_id: int):
    """
    Handles servicing the landing page.
    :param qr_id: qr code id distinguishing specific group of qr codes
    :return:
    """

    resp = make_response(render_template('landing.html', qr_id=qr_id))

    if request.method == 'POST':
        vote_id = add_vote_record(db, request.form, request.cookies)
        resp.set_cookie('vote_id', str(vote_id))

    return resp

@app.route('/<int:qr_id>/qr', methods=['GET'])
def qrcode(qr_id: int):
    data = "movetogether.now/" + str(qr_id)
    img = make(data)

    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    img_bin = base64.b64encode(buffer.getvalue()).decode('ascii')

    return '<img src="data:image/jpeg;base64,' + img_bin + '"/>'

@app.route("/setqrloc", methods=['GET', 'POST'])
def set_qr_loc():
    if request.method == 'POST':
        add_loc_record(db, request.form)

    return render_template('set_qr_loc.html')



if __name__ == '__main__':
    db = sqlite3.connect("../myfuckingdb.db", check_same_thread=False)
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS qr2loc (id INTEGER PRIMARY KEY AUTOINCREMENT, lat FLOAT, lng FLOAT);")
    cur.execute("CREATE TABLE IF NOT EXISTS vote2qr (id INTEGER PRIMARY KEY AUTOINCREMENT, response TEXT, qr_id INTEGER);")
    cur.close()

    app.run(host="127.0.0.1", port=8000, debug=True)