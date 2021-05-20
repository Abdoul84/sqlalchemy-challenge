#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 14 13:10:55 2021

@author: moz
"""


import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

# db setup and error check
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing db into a new model
base = automap_base()

# reflect the tables 
base.prepare(engine,reflect=True)

# Save references to each table
Measurement = base.classes.measurement
Station = base.classes.station

# session link
session = Session(engine)

# Flask
app = Flask(__name__)

# Flask Routes
#List all routes that are available
@app.route("/")
def Home():

     return (
         f"/api/v1.0/precipitation<br/>"
         f"/api/v1.0/stations<br/>"
         f"/api/v1.0/temperatures<br/>"
         f"/api/v1.0/<start><br/>"
         f"/api/v1.0/<start>/<end><br/>"
     )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last data point in the database
    last_year_precip = session.data(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    #find date 12 months before
    prior_year = dt.datetime.strptime(last_year_precip, "%Y-%m-%d") - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    data = session.data(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prior_year).all()

    precip_value = []
    for i, prcp in data:
        data = {}
        data['date'] = i
        data['prcp'] = prcp
        precip_value.append(data)

    return jsonify(precip_value)


@app.route("/api/v1.0/stations")
def stations():
    
    data = session.data(Station.name, Station.stations, Station.elevation).all()

    #create dictionary for JSON
    stations_list = []
    for i in data:
        row = {}
        row['name'] = i[0]
        row['stations'] = i[1]
        row['elevation'] = i[2]
        stations_list.append(row)
    return jsonify(stations_list)

@app.route("/api/v1.0/temperatures")
def temperature_temperatures():
    data = session.data(Station.name, Measurement.date, Measurement.temperatures).\
        filter(Measurement.date >= "2017-01-01", Measurement.date <= "2018-01-01").\
        all()

    #use dictionary, create json
    temps_list = []
    for i in data:
        row = {}
        row["Date"] = i[1]
        row["stations"] = i[0]
        row["Temperature"] = int(i[2])
        temps_list.append(row)

    return jsonify(temps_list)


@app.route("/api/v1.0/<start>")
def start(start=None):
    
    from_start = session.data(Measurement.date, func.min(Measurement.temperatures), func.avg(Measurement.temperatures),
                               func.max(Measurement.temperatures)).filter(Measurement.date >= start).group_by(
        Measurement.date).all()
    from_start_list = list(from_start)
    return jsonify(from_start_list)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    ranges = session.data(Measurement.date, func.min(Measurement.temperatures), func.avg(Measurement.temperatures),
                                  func.max(Measurement.temperatures)).filter(Measurement.date >= start).filter(
        Measurement.date <= end).group_by(Measurement.date).all()
    ranges_list = list(ranges)
    return jsonify(ranges_list)

if __name__ == "__main__":
    app.run(debug=False)
