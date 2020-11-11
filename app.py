# Import dependencies
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Set up the database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect the existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session from Python to the DB
session = Session(engine)

#Set up Flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    print("Server received request for 'Home' page...")
    return (
        f"<h2>Welcome to the Climate API!<br></h2>"
        f"<u>Available Routes:</u><br><br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start_date/<start_date><br>"
        f"/api/v1.0/start_end_date/<start_date>/<end_date><br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")
    results = session.query(Measurement.date, Measurement.prcp).all() 
    
    all_precip = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precip.append(precipitation_dict)

    return  jsonify(all_precip)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    
    results = session.query(Station.station, Station.name).all()
    all_names = list(np.ravel(results))
    return  jsonify(results)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').all() 
        
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["Temp observation"] = tobs
        all_tobs.append(tobs_dict)

    return  jsonify(all_tobs)

@app.route("/api/v1.0/start_date/<start_date>")
def start(start_date):
    print("Server received request for 'start_date' page...")
    results = session.query(Measurement.tobs).filter(Measurement.date >= start_date).all() 
    sum = 0
    min_temp = 1000
    max_temp = 0
    count = 0

    for tobs in results:
        tobs = tobs[0]
        
#check for new max or min
        if tobs < min_temp:
            min_temp = tobs
        if tobs > max_temp:
            max_temp = tobs
        
        sum = sum + tobs
        count = count + 1

#division by 0 test
    try:
        avg_temp = sum/count
    except:
        avg_temp = -1

#return the avg, max, & min temp within the date range
    return 'Min, avg, max are {} {} {}'.format(min_temp, avg_temp, max_temp)

@app.route("/api/v1.0/start_end_date/<start_date>/<end_date>")
def start_end(start_date, end_date):
    print("Server received request for 'start_end_date' page...")
    results = session.query(Measurement.tobs).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all() 
    
    sum = 0
    min_temp = 1000
    max_temp = 0
    count = 0

    for tobs in results:
        tobs = tobs[0]
        
#check for new max or min
        if tobs < min_temp:
            min_temp = tobs
        if tobs > max_temp:
            max_temp = tobs
        
        sum = sum + tobs
        count = count + 1

#division by 0 test
    try:
        avg_temp = sum/count
    except:
        avg_temp = -1

#return the avg, max, & min temp within the date range
    return 'Avg, max, min are {} {} {}'.format(avg_temp, max_temp, min_temp)


if __name__ == "__main__":
    app.run(debug=True)