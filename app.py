from flask import Flask, jsonify
import datetime as dt

from dateutil.relativedelta import relativedelta

import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

#set up server

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#set up routes
@app.route("/")
def index():
    return ("<h1>Available Routes</h1>"
            "<h2>Dates in YYYY-MM-DD format</h2>"
            "<ul>"
            "<li>/api/v1.0/precipitation : </li>"
            "<ul><li>Result: Dictionary of date keys and total precipitation values.</li></ul>"
            "<li>/api/v1.0/stations</li>"
            "<ul><li>Result: List of station dictionaries {ID: [name, Latitude, longitude, elevation]</li></ul>"
            "<li>/api/v1.0/tobs</li>"
            "<ul><li>Result: List of all temps from the last year.</li></ul>"
            "<li>/api/v1.0/[start_date]</li>"
            "<ul><li>Result: min temp, max temp, average temp</li></ul>"
            "<li>/api/v1.0/[start_date]/[end_date]</li>"
            "<ul><li>Result: min temp, max temp, average temp</li></ul>"
            "</ul>")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    data = session.query(Measurement.date, func.sum(Measurement.prcp).label('total')).group_by(Measurement.date).all()
    session.close()
    data_dict = {}
    for row in data:
        data_dict[row.date] = round(row.total,2)
    return jsonify(data_dict)

@app.route("/api/v1.0/stations")
def stations():
    session =  Session(engine)
    data = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()
    data_list = []
    for row in data:
        data_list.append({row.station: [row.name, row.latitude, row.longitude, row.elevation]})
    return jsonify(data_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = dt.date.fromisoformat(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0])
    one_year_ago = last_date - relativedelta(years = 1)
    stations_all = session.query(Measurement.station).all()
    station_df = pd.Series([station[0] for station in stations_all])
    top_station = station_df.value_counts().index.tolist()
    last_year_data = session.query(Measurement.tobs
                    ).filter(Measurement.date > str(one_year_ago)
                    ).filter(Measurement.station == top_station[0]
                    ).all()
    session.close()
    return jsonify([row[0] for row in last_year_data])

@app.route("/api/v1.0/<start>")
def start(start):
    sel = [
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ]
    session = Session(engine)
    result = session.query(*sel).filter(Measurement.date > start).all()
    session.close()
    return jsonify(result)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    sel = [
        func.min(Measurement.tobs),
        func.max(Measurement.tobs),
        func.avg(Measurement.tobs)
    ]
    session = Session(engine)
    result = session.query(*sel).filter(Measurement.date > start).filter(Measurement.date < end).all()
    session.close()
    return jsonify(result)



if __name__ == "__main__":
    app.run(debug=True)