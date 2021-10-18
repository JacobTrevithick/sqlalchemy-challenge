
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, json, jsonify

# initialize flask app
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
    
    '''
    Home page for the Flask app. Returns available api paths.
    '''
    
    return (
        f"Welcome to the Climate App API home page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart_date&gt<br/>"
        f"/api/v1.0/&ltstart_date&gt/&ltend_date&gt<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' page...")
    
    '''
    Returns precipitation values for all recorded dates (includes NULLs)
    Sorted in descending order (earliest date first)
    '''
    
    # Open session
    session = Session(engine)
    # Query dates and precipitation results in descedning date order,
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()
    # close session.
    session.close()
    
    #  aggregate data in to dictionary to be jsonified and returned to user.
    all_prec = []
    for date, prcp in results:
        prec_dict = {}
        prec_dict[date] = prcp
        all_prec.append(prec_dict)

    return jsonify(all_prec)



@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'stations' page...")
    
    '''
    Returns all stations listed in the stations DB table
    '''
    
    # Open session
    session = Session(engine)

    # Query all station information from Station table.
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    
    results = session.query(*sel).all()
    
    # close session
    session.close()
    
    #  aggregate data in to dictionary to be jsonified and returned to user.
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

    '''
    Returns temperature recordings for the last year at the most active station.
    '''

    # Open session
    session = Session(engine)
   
    # query most active station and most recent date in DB
    mst_act_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).limit(1).all()[0][0]
    most_recent_date = session.query(Measurement.date).filter(Measurement.station == mst_act_station).order_by(Measurement.date.desc()).limit(1).all()[0][0]
    
    # convert most_recent_date to start_date date object and calculate end_date for 1 year of tobs recordings.
    start_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    end_date = start_date - dt.timedelta(days=365)
    
    # Query results for date/tobs info for most active station in the last year.
    results = session.query(Measurement.date, Measurement.tobs).filter((Measurement.station == mst_act_station) & (Measurement.date >= end_date)).all()
    
    # close session
    session.close()
    
    #  aggregate data in to dictionary to be jsonified and returned to user.
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict['station_id'] = mst_act_station
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    print("Server received request for 'start_date' page...")
    
    '''
    Function will be called when only the start date is given.
    Returns the min, avg, and max temperature observations for all dates on and after the start_date
    '''
    
    # Converted given start_date to canonicalized form. Error if given in incorrect formatting.
    try:
        canonicalized = dt.datetime.strptime(start_date.replace(" ", ""), '%Y-%m-%d').date()
        print(canonicalized)
    except:
        return "Oops, the date you entered is not in the correct format. Please enter dates in YYYY-MM-DD format."
    
    # open session
    session = Session(engine)
    
    # query most recent date
    most_recent_date = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1).all()[0][0], '%Y-%m-%d').date()
    
    # check to see if given start_date is in dataset.
    if canonicalized >  most_recent_date:
        return f"The date you have entered is not included in the dataset. Please use a date before {most_recent_date}"
    
    # query min, avg, and max temperature observations for all dates after start_date (inclusive)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= canonicalized).all()

    #  aggregate data in to dictionary to be jsonified and returned to user.
    all_tobs = []
    tobs_dict = {}
    
    tobs_dict['start_date'] = str(canonicalized)
    tobs_dict['minimum_temp'] = results[0][0]
    tobs_dict['average_temp'] = round(results[0][1], 2)
    tobs_dict['maximum_temp'] = results[0][2]
    all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)


@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date(start_date, end_date):
    print("Server received request for 'start_date/end_date' page...")
    
    '''
    Function will be called when the start and end date are given.
    Returns the min, avg, and max temperature observations for all dates between start_date(inclusive) and end_date(inclusive)      
    '''
    
    # Converted given start_date and end_date to canonicalized form. Error if given in incorrect formatting.
    try:
        canonicalized_sd = dt.datetime.strptime(start_date.replace(" ", ""), '%Y-%m-%d').date()
        canonicalized_ed = dt.datetime.strptime(end_date.replace(" ", ""), '%Y-%m-%d').date()
    except:
        return "Oops, the date(s) you entered is not in the correct format. Please enter dates in YYYY-MM-DD format."
    
    # open session
    session = Session(engine)
    
    # check start_date isn't after end_date and both dates are within the dataset.
    most_recent_date = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1).all()[0][0], '%Y-%m-%d').date()
    earliest_date = dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.asc()).limit(1).all()[0][0], '%Y-%m-%d').date()
    
    if canonicalized_sd >  most_recent_date or canonicalized_sd < earliest_date:
        return f"The date(s) you have entered is not included in the dataset. Please use a dates in the range {earliest_date} to {most_recent_date}"
    elif canonicalized_ed >  most_recent_date or canonicalized_ed < earliest_date:
        return f"The date(s) you have entered is not included in the dataset. Please use a dates in the range {earliest_date} to {most_recent_date}"
    elif canonicalized_sd > canonicalized_ed:
        return f"The end date you have entered is earlier than the start date. Please choose new dates in the range {earliest_date} to {most_recent_date}"
    
    # query min, max, and avg temperature observations for the given date range.
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter((Measurement.date >= canonicalized_sd) & (Measurement.date <= canonicalized_ed)).all()
    print(results)

    #  aggregate data in to dictionary to be jsonified and returned to user.
    all_tobs = []
    tobs_dict = {}
    
    tobs_dict['start_date'] = str(canonicalized_sd)
    tobs_dict['end_date'] = str(canonicalized_ed)
    tobs_dict['minimum_temp'] = results[0][0]
    tobs_dict['average_temp'] = round(results[0][1],2)
    tobs_dict['maximum_temp'] = results[0][2]
    all_tobs.append(tobs_dict)
    
    return jsonify(all_tobs)

if __name__ == "__main__":
    app.run(debug=True)
