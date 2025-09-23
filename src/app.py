import base64
import sqlite3
from io import BytesIO


from flask import Flask, render_template, request, make_response, redirect, url_for
from qrcode.main import make

from dbhandler import add_vote_record, add_loc_record, add_email_record



db = sqlite3.connect("../myfuckingdb.db", check_same_thread=False)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS qr2loc (id INTEGER PRIMARY KEY AUTOINCREMENT, lat FLOAT, lng FLOAT);")
cur.execute("CREATE TABLE IF NOT EXISTS vote2qr (id INTEGER PRIMARY KEY AUTOINCREMENT, response TEXT, qr_id INTEGER);")
cur.execute("CREATE TABLE IF NOT EXISTS email_signups (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, vote_id INTEGER);")
cur.close()


app = Flask(__name__)


@app.route('/thank_you')
def thanks():
    return render_template('thank_you.html', show_email = request.cookies['show_email_form'])

@app.route('/loc')
def set_loc():
    return render_template('set_qr_loc.html')


@app.route("/<int:qr_id>", methods=['GET', 'POST'])
def landing(qr_id: int):
    if request.method == 'POST':
        # Handle the vote submission
        vote_id = add_vote_record(db, request.form, request.cookies)

        resp_val = (request.form.get('response') or '').strip().lower()
        show_email = '1' if resp_val in ('yes') else '0'

        
        # Create redirect response
        resp = make_response(redirect('/thank_you'))
        resp.set_cookie('vote_id', str(vote_id))
        resp.set_cookie('show_email_form', show_email)

        return resp
    
    # Handle GET request - show the voting form
    return render_template('landing.html', qr_id=qr_id)

@app.route('/<int:qr_id>/qr', methods=['GET'])
def qrcode(qr_id: int):
    data = "https://movetogether.now/" + str(qr_id)
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

@app.route('/save_email', methods=['POST'])
def save_email():
    # save posted email; vote_id (if available) is read from cookies inside add_email_record
    add_email_record(db, request.form, request.cookies)
    resp = make_response(redirect(url_for('thanks')))
    resp.set_cookie('show_email_form', '0')
    return resp


if __name__ == '__main__':

    app.run(host="127.0.0.1", port=8000, debug=True)