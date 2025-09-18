from werkzeug.datastructures import ImmutableMultiDict
import sqlite3




def add_vote_record(db, form: ImmutableMultiDict):
    print(form)
    qr_id = form['qr_id']
    taiwan = form['taiwan']




def add_loc_record(db, form: ImmutableMultiDict):
    print(form)
    lat = form['lat']
    lng = form['lng']
    qr_id = form['qr_id']
    print(lat, lng, qr_id)