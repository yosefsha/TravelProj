from flask import Flask, url_for, request,  render_template, redirect, jsonify
from app import app
from flask_googlemaps import GoogleMaps
#from pip._vendor import requests
import requests


googlekey = "AIzaSyAkcXsDGhKO0xEo2odUYvWlUas2yv2gSaE"
distanceurl = "https://maps.googleapis.com/maps/api/distancematrix/json"
TimeParam = 2/3
TaxiStartTarif = 12.8
TaxiPerMeter = 0.005
BusRide = 6.9
CarCostPerMeter = 0.0009

@app.route('/')
def hello():
    return redirect('/calculate')


@app.route('/calculate')
def calculate():
   return render_template("TravelInputMap.html");


@app.route('/calc_distance')
def calc_distance():
    #get data from client
    originlat = request.args.get('originlat')
    originlong = request.args.get('originlong' )
    destlat = request.args.get('destlat')
    destlong = request.args.get('destlong' )
    wage = request.args.get('wage' )
    origin = originlat + ',' + originlong
    destination = destlat + ',' + destlong 
    #build params dictionary from request:
    orgdestparams = {'units': 'imperial',
                 'origins': origin,
                 'destinations': destination,
                 'key': googlekey }

    carres = getCarCost(orgdestparams, wage)
    busres = getBusCost(orgdestparams, wage)
    footres = getFootCost(orgdestparams, wage)
    taxires = getTaxiCost(orgdestparams, wage)
    return jsonify(carres = carres,
                    busres = busres,
                    footres = footres,
                    taxires = taxires)

#helper funcs:
def getCarCost(orgdestparams, wage =0):
    orgdestparams['mode'] = 'driving'
    try:
        res = requests.get(distanceurl, params = orgdestparams)
        jsonres = res.json() 
        distance = float(jsonres['rows'][0]['elements'][0]['distance']['value'])
        duration = float(jsonres['rows'][0]['elements'][0]['duration']['value'])
        floatwage = float(wage)
    except Exception as e:
        print("Unexpected error")
        print(e)
        return 100000
    duration = duration/3600
    return distance * CarCostPerMeter + duration * TimeParam * floatwage

def getBusCost(orgdestparams, wage = 0):
    orgdestparams['mode'] = 'transit'
    try:
        res = requests.get(distanceurl, params = orgdestparams)
        jsonres = res.json()
        distance = float(jsonres['rows'][0]['elements'][0]['distance']['value'])
        duration = float(jsonres['rows'][0]['elements'][0]['duration']['value'])
        floatwage = float(wage)
    except Exception as e:
        print("Unexpected error")
        print(e)
        return 100000
    duration = duration/3600
    return TimeParam * floatwage * duration + BusRide

def getFootCost(orgdestparams, wage ):
    orgdestparams['mode'] = 'walking'
    try:
        res = requests.get(distanceurl, params = orgdestparams)
        jsonres = res.json()
        distance = float(jsonres['rows'][0]['elements'][0]['distance']['value'])
        duration = float(jsonres['rows'][0]['elements'][0]['duration']['value'])
        duration = duration/3600
        floatwage = float(wage)
    except Exception as e:
        print("Unexpected error")
        print(e)
        return 100000

    return TimeParam * floatwage * duration
    

#def getTaxiCost(originlat, originlong, destlat, destlong):
def getTaxiCost(orgdestparams, wage = 0):
    orgdestparams['mode'] = 'driving'
    try:
        res = requests.get(distanceurl, params = orgdestparams)
        jsonres = res.json()
        distance = float(jsonres['rows'][0]['elements'][0]['distance']['value'])
        duration = float(jsonres['rows'][0]['elements'][0]['duration']['value'])
        duration = duration/3600
        floatwage = float(wage)
    except Exception as e:
        print("Unexpected error")
        print(e)
        return 100000


    return TimeParam * floatwage * duration + distance * TaxiPerMeter + TaxiStartTarif


