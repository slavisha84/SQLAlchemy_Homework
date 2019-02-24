
###################################################################################################
# Importing dependencies for comunicating with sqlite db
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine,inspect, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# Importing dependencies for data analysis
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib
from matplotlib import style
style.use('seaborn')
import matplotlib.pyplot as plt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Hawaii.sqlite")

# reflect the database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurs = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")

def home():
	print("Server received request for 'Home' page.")
	return "Welcome to the Surfs Up Weather API!"

@app.route("/welcome")
#List all available routes
def welcome ():
	return (
		f"Welcome to the Surf Up API<br>"
		f"Available Routes:<br>"
		f"/api/v1.0/precipitation<br>"
		f"/api/v1.0/stations<br>"
		f"/api/v1.0/tobs<br>"
		f"/api/v1.0/<start><br>"
		f"/api/v1.0<start>/<end><br>"
	)
#########################################################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of rain fall for prior year"""
# Creating the query to identify last date to identify end ponint of the year

    ld = session.query(Measurs.date).order_by(Measurs.date.desc()).first()

# print(ld) returns '2017-08-23' which means we will be working with peroiod between 2016-8-23 and 2017-8-23
    precip_year = session.query(Measurs.date, Measurs.prcp).filter(Measurs.date >= '2016-8-23').order_by(Measurs.date).all()

# Create a list of dicts with `date` and `prcp` as the keys and values

    precipitation = []
    for x in precip_year:
        row = {}
        row["date"] = precip_year[0]
        row["prcp"] = precip_year[1]
        precipitation.append(row)

    return jsonify(precipitation)

#########################################################################################
# Create a dictionary from the row data and append to a list of all_stations.
@app.route("/api/v1.0/stations")
def stations():
    stations_qry = session.query(Station.name, Station.station)
    stations = pd.read_sql(stations_qry.statement, stations_qry.session.bind)
    return jsonify(stations.to_dict())

#########################################################################################

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a json list of Temperature Observations (tobs) for the previous year"""
    # Query all the stations and for the given date. 
    temp = session.query(Measurs.station, Measurs.date, Measurs.tobs).\
                    group_by(Measurs.date).\
                    filter(Measurs.date > '2016-8-23').\
                    order_by(Measurs.station).all()
                    
    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_data = []
    for tobs_data in temp:
        tobs_data_dict = {}
        tobs_data_dict["Station"] = tobs_data.station
        tobs_data_dict["Date"] = tobs_data.date
        tobs_data_dict["Temperature"] = tobs_data.tobs
        temp_data.append(tobs_data_dict)
    
    return jsonify(temp_data)

#########################################################################################
@app.route("/api/v1.0/temp/<start>")
def start_stats(start=None):
    """Return a json list of the minimum temperature, the average temperature, and the
    max temperature for a given start date"""
    # Query all the stations and for the given date. 
    stats = session.query(func.min(Measurs.tobs), func.max(Measurs.tobs),func.avg(Measurs.tobs)).\
    filter(Measurs.date >= start).all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
    temp_stats = []
    
    for Tmin, Tmax, Tavg in stats:
        temp_stats_dict = {}
        temp_stats_dict["Minimum Temp"] = Tmin
        temp_stats_dict["Maximum Temp"] = Tmax
        temp_stats_dict["Average Temp"] = Tavg
        temp_stats.append(temp_stats_dict)
    
    return jsonify(temp_stats)
    

@app.route("/api/v1.0/temp/<start>/<end>")
def calc_stats(start=None, end=None):
    """Return a json list of the minimum temperature, the average temperature, 
    and the max temperature for a given start-end date range."""
    
    # Query all the stations and for the given range of dates. 
    calc = session.query(func.min(Measurs.tobs), func.max(Measurs.tobs),func.avg(Measurs.tobs)).\
    filter(Measurs.date >= start).filter(Measurs.date <= end).all()

    # Create a dictionary from the row data and append to a list of for the temperature data.
    begin_end_stats = []
    
    for Tmin, Tmax, Tavg in calc:
        begin_end_stats_dict = {}
        begin_end_stats_dict["Minimum Temp"] = Tmin
        begin_end_stats_dict["Maximum Temp"] = Tmax
        begin_end_stats_dict["Average Temp"] = Tavg
        begin_end_stats.append(begin_end_stats_dict)
    
    return jsonify(begin_end_stats)

#########################################################################################

if __name__ == "__main__":
    app.run(debug=True)