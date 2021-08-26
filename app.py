import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn=engine.connect()
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement_class = Base.classes.measurement
station_class=Base.classes.station

session=Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/r>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # most_recent = session.query(measurement_class.date).\
    #     order_by(measurement_class.date.desc()).first()
    
    # year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)
   
    results= session.query(measurement_class.date, measurement_class.prcp).filter(measurement_class.date > '2016-08-23').order_by(measurement_class.date).all()


    rain_total=[]
    for result in results:
        row={}
        row["date"]=result[0]
        row["prcp"]=result[1]
        rain_total.append(row)

    return jsonify(rain_total)

@app.route("/api/v1.0/stations")
def stations():
    stations_query=session.query(station_class.name,station_class.station)
    stations = pd.read_sql(stations_query.statement,stations_query.session.bind)
    return jsonify(stations.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    most_recent = session.query(measurement_class.date).\
        order_by(measurement_class.date.desc()).first()
    
    year_ago = dt.date(2017,8,23)-dt.timedelta(days=365)

    temperatures=session.query(measurement_class.station,measurement_class.date,measurement_class.tobs).\
        filter(measurement_class.station==most_active).\
        filter(measurement_class.date>year_ago).\
        order_by(measurement_class.date).all()

    temperature_total=[]
    for row in temperatures:
        row={}
        row["date"]=temperatures[0]
        row["tobs"]=temperatures[1]
        temperature_total.append(row)

    return jsonify(temperature_total)

@app.route("/api/v1.0/<start>")
def start_date(start):
    start_date=dt.datetime.strptime(start, '%Y-%m-%d')
    last_year=dt.timedelta(days=365)
    start=start_date-last_year
    end= dt.date(2017,8,23)
   
    first_query=session.query(func.min(measurement_class.tobs), func.avg(measurement_class.tobs),\
        func.max(measurement_class.tobs)).filter(measurement_class.date >= start).\
        filter(measurement_class.date <=end).all()
    
    query_list=list(np.ravel(first_query))
    return jsonify(query_list)   
            
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    start_date=dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end, '%Y-%m-%d')
    last_year=dt.timedelta(days=365)
    start=start_date-last_year
    end= end_date-last_year

    first_query=session.query(func.min(measurement_class.tobs), func.avg(measurement_class.tobs),\
        func.max(measurement_class.tobs)).filter(measurement_class.date >= start).\
        filter(measurement_class.date <=end).all()

    query_list=list(np.ravel(first_query))
    return jsonify(query_list)




if __name__ == '__main__':
    app.run(debug=True)
