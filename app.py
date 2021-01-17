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
   #create route with hyperlink as a little bonus
    return (
        f"Available Routes:<br/>"
        f"<a href=\"/api/v1.0/precipitation\">/api/v1.0/precipitation</a> - Returning: precipitation by day for last year of data<br/>"
        f"<a href=\"/api/v1.0/stations\">/api/v1.0/stations</a> - Returning: names of all stations<br/>"
        f"<a href=\"/api/v1.0/tobs\">/api/v1.0/tobs</a> - Returning: temps for last year of data for most active station<br/>"
        f"<a href=\"/api/v1.0/start\">/api/v1.0/yyyy-mm-dd</a> - Returning: Tmin, Tavg, Tmax<br/>"
        f"<a href=\"/api/v1.0/start/end\">/api/v1.0/yyyy-mm-dd/yyyy-mm-dd</a> - Returning: Tmin, Tavg, Tmax"

    )


@app.route("/api/v1.0/precipitation")
def Precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    # Query last year data
    lastyear = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    yearquery = dt.datetime.strptime(lastyear[0], '%Y-%m-%d') - dt.timedelta(days = 365)
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
    results =  session.query(Station).all()
    session.close()

    # Create a list of station names using the name column
    station_list = []
    for row in results:
       station_list.append(row.name)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def Tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query the dates and temperature observations of the most active station for the last year of data."""
    #query prior year
    lastyear = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    yearquery = dt.datetime.strptime(lastyear[0], '%Y-%m-%d') - dt.timedelta(days = 365)
    # Query most active station
    most_active = session.query(Measurement.station).group_by(Measurement.station).\
        order_by(func.count(Measurement.date).desc()).first()
    #query most active station for prior year
    high_station = session.query(Measurement.tobs).filter(Measurement.station==most_active[0]).\
    filter(Measurement.date >= yearquery).all()

    session.close()

    # JSON list of temps observed for prior year
    temp_list = []
    for row in high_station:
       temp_list.append(row.tobs)

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def StartEnd(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    # Query with start and end date
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    return jsonify(result)

@app.route("/api/v1.0/<start>")
def Start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query with start date only
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    
    session.close()

    return jsonify(result)    

if __name__ == '__main__':
    app.run(debug=True)
