from werkzeug.datastructures import ImmutableMultiDict
import sqlite3


def add_vote_record(db: sqlite3.Connection, form: ImmutableMultiDict, cookies: ImmutableMultiDict):
    print(form)
    qr_id = form['qr_id']
    taiwan = form['response']

    cur = db.cursor()
    cur.execute("select IFNULL(MAX(seq), 0) from sqlite_sequence where name=?", ('vote2qr',))
    (row,) = cur.fetchone()

    # TODO: error handling if cookie is not valid int
    vote_id = int(cookies.get('vote_id', default=str(row + 1)))

    cur.execute("INSERT INTO vote2qr (id, response, qr_id) VALUES (?, ?, ?) ON CONFLICT DO UPDATE SET response = ?;",
                (vote_id, taiwan, qr_id, taiwan))
    cur.close()
    db.commit()

    return vote_id


def add_loc_record(db: sqlite3.Connection, form: ImmutableMultiDict):
    print(form)
    lat = form['lat']
    lng = form['lng']
    qr_id = form['qr_id']
    print(lat, lng, qr_id)
