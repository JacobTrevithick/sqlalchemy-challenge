
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


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
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>"
    )

# ######################
# TODO: precipation route

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' page...")
    
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc())
    
    prec_dict = {}
    for row in results:
        prec_dict[row[0]] = row[1]
    
    return jsonify(prec_dict)


# ######################
# TODO: stations route

# ######################
# TODO: tobs route

# ######################
# TODO: start and end date route






if __name__ == "__main__":
    app.run(debug=True)
