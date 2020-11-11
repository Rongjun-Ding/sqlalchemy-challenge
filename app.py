# Import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, MetaData
from sqlalchemy.pool import StaticPool
from flask import Flask, jsonify
import logging
import datetime as dt
import re
from operator import itemgetter

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
# Home page.
# List all routes that are available.
def welcome():
    return (
        f"Welcome to the Climate APP API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start><br/>"
        f"/api/v1.0/start_end_date/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
def precipitation():
    
    results = session.query(Measurement.date, Measurement.prcp).all() 
    
    all_precip = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precip.append(precipitation_dict)

    return  jsonify(all_precip)

@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.
def stations():
    
    
    results = session.query(Station.station, Station.name).all()
    station_list = []
    for row in results:
        station_dict = {}
        station_dict['station'] = row.station
        station_dict['name'] = row.name
        station_list.append(station_dict)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
def tobs():
    last_date_query = session.query(func.max(Measurement.date))
    for record in last_date_query:
        last_date = record 
        print(last_date)
    last_date_string = str(last_date)

    match = re.search('\d{4}-\d{2}-\d{2}', last_date_string)

    last_date = dt.datetime.strptime(match.group(), '%Y-%m-%d').date()
    last_year = last_date - dt.timedelta(days=365)

    station_query = session.query(Measurement.station,func.count(Measurement.date)).group_by(Measurement.station).\
                                              order_by(func.count(Measurement.date).desc())

    result = [r.station for r in station_query]
    most_active_station = result[0]
    sel_tobs = [Measurement.station,Measurement.date,Measurement.tobs]

    query_tobs = session.query(*sel_tobs).filter(Measurement.date >= last_year).filter(Measurement.station == most_active_station)
    data_tobs = query_tobs.all()
    
    tobs_list = []
    for row in data_tobs:
        tobs_dict = {}
        tobs_dict['station'] = row.station
        tobs_dict['date'] = row.date
        tobs_dict['tobs'] = row.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/start_date/<start>")
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
def start(start):
    start_date_query = session.query(func.max(Measurement.date))
    for record in start_date_query:
        start = record 
        print(start)
    start_date_query = str(start)

    match1 = re.search('\d{4}-\d{2}-\d{2}', start_date_query)

    start = dt.datetime.strptime(match1.group(), "%Y-%m-%d").date()
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    start_date_query = session.query(func.min(Measurement.tobs).label('tmin'), func.avg(Measurement.tobs).label('tavg'), func.max(Measurement.tobs).label('tmax')).\
                        filter(Measurement.date >= start).all()

    st_date_list = []
    for row in start_date_query:
        calc_temp_s = {}
        calc_temp_s['tmin'] = row.tmin
        calc_temp_s['tavg'] = row.tavg
        calc_temp_s['tmax'] = row.tmax
        st_date_list.append(calc_temp_s)
    return jsonify(st_date_list)


@app.route("/api/v1.0/start_end_date/<start>/<end>")
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
def start_end(start, end):
    start = dt.datetime.strptime("2017-2-20", "%Y-%m-%d").date()
    end = dt.datetime.strptime("2017-2-26", "%Y-%m-%d").date()
    results = session.query(Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end).all() 
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
    return jsonify(avg_temp, max_temp, min_temp)
    #return 'Avg, max, min are {}  {}  {}'.format(avg_temp, max_temp, min_temp)


if __name__ == "__main__":
    app.run(debug=True)