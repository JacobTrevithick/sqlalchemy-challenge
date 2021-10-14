
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, json, jsonify


app = Flask(__name__)

# create engine to hawaii.sqlite
database_path = "Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect = True)

# Assign references to database models
Measurement = Base.classes.measurement
Station = Base.classes.station


@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to the Climate App API home page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/< start_date ><br/>"
        f"/api/v1.0/< start_date >/< end_date ><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' page...")
    
    '''
    Returns precipitation values for all recorded dates (includes NULLs)
    Sorted in descending order (earliest date first)
    '''
    
    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()
    
    session.close()
    
    all_prec = []
    for date, prcp in results:
        prec_dict = {}
        prec_dict[date] = prcp
        all_prec.append(prec_dict)

    return jsonify(all_prec)



@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page...")

    session = Session(engine)

    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    
    results = session.query(*sel).all()
    
    session.close()
    
    all_stations = []
    for station, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict['station_id'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")

    session = Session(engine)
   
    mst_act_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).limit(1).all()[0][0]
    
    most_recent_date = session.query(Measurement.date).filter(Measurement.station == mst_act_station).order_by(Measurement.date.desc()).limit(1).all()[0][0]
    
    start_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    
    end_date = start_date - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == mst_act_station) & (Measurement.date >= end_date)).all()
    
    session.close()
    
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['station_id'] = mst_act_station
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


# ######################
# TODO: start and end date route






if __name__ == "__main__":
    app.run(debug=True)
