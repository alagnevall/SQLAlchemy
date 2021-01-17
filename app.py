import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
connection = engine.connect()
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def Home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"

    )


@app.route("/api/v1.0/precipitation")
def Precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    # Query last year data
    # lastyear = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    yearquery = dt.date(2017,8,23) - dt.timedelta(days = 365)
    results = session.query(Measurement.date, Measurement.prcp ).\
        filter(Measurement.date >= yearquery).all()

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    prcp_dict = {}
    for date, prcp in results:
        prcp_dict[date] = prcp        

    return jsonify(prcp_dict)
   
   
@app.route("/api/v1.0/stations")
def Stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    results =  session.query(Station)
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    station_list = []
    for row in results:
       station_list.append(row.station)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def Tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data."""
    #query prior year
    yearquery = dt.date(2017,8,23) - dt.timedelta(days = 365)
    # Query most active station
    most_active = session.query(Measurement.station).group_by(Measurement.station).\
        order_by(func.count(Measurement.date).desc()).first()
    #query most active station for prior year
    high_station = session.query(Measurement.tobs).filter(Measurement.station==most_active[0]).\
    filter(Measurement.date >= yearquery).all()

    session.close()

#     # JSON list of temps observed for prior year
    temp_list = []
    for row in high_station:
       temp_list.append(row.tobs)

    return jsonify(temp_list)

# @app.route("/api/v1.0/<start>")
# def names():
#     # Create our session (link) from Python to the DB
#     session = Session(engine)

#     """Return a list of all passenger names"""
#     # Query all passengers
#     results = session.query(Passenger.name).all()

#     session.close()

#     # Convert list of tuples into normal list
#     all_names = list(np.ravel(results))

#     return jsonify(all_names)

if __name__ == '__main__':
    app.run(debug=True)
