from flask import Flask, jsonify, request, abort
from pymongo import MongoClient
from geopy.geocoders import Nominatim
import RegionFinder
import pickle
import pandas as pd
import random
import requests

app=Flask(__name__)

def getRegionFromAddress(address):
    geolocation=Nominatim(user_agent="example")
    location=geolocation.geocode(address)
    if location:
        locationCoordinates={'lat':location.latitude,'lng':location.longitude}
        print(locationCoordinates)
        # print(locationCoordinates)
        # print(RegionFinder.findRegion(locationCoordinates))
        return RegionFinder.findRegion(locationCoordinates)

def getAddressDetails(address):
    geolocation=Nominatim(user_agent="example")
    location=geolocation.geocode(address)
    if location:
        addressDetails={'latitude':location.latitude,'longitude':location.longitude}
        requestBody={'group_id':"-1558704",'lat':addressDetails['latitude'],'lng':addressDetails['longitude']}
        response=requests.post("https://www.zumper.com/api/x/1/location_scores",requestBody)
        if response.status_code==200:
            scoreResponse=response.json()
            # Extract the transit score and walk score values
            addressDetails['transitScore'] = round(scoreResponse["scores_json"]["transit_friendly"]["value"])*2
            addressDetails['walkScore'] = round(scoreResponse["scores_json"]["pedestrian_friendly"]["value"]*10*2)
        else:
            addressDetails['transitScore']=round(random.uniform(1,11))
            addressDetails['walkScore']=round(random.uniform(1,101))
        return addressDetails
            

@app.route('/rental/getCompetitorRates', methods=['GET'])
def getCompetitorRates():
    address=request.args.get("address")
    unitType=request.args.get("unitType")
    if address is None:
        abort(400, description='Mandatory query parameter: address not provided')
    elif unitType is None:
        abort(400, description='Mandatory query parameter: unitType not provided')
    mongoUri="mongodb://localhost:27017"
    mongoDatabase="RentalProject"
    mongoCollectionName="RentalData"
    mongoClient=MongoClient(mongoUri)
    mongoDb=mongoClient[mongoDatabase]
    mongoCollection=mongoDb[mongoCollectionName]
    region=getRegionFromAddress(address)
    builders=mongoCollection.distinct("PROPERTY_OWNER")
    builderApiResponse=[]
    for builder in builders:
        # print(builder)
        result=mongoCollection.find({'$and':[{'PROPERTY_OWNER':builder},{'SUITE_TYPE':unitType},{'DISTRICT_REGION':region}]})
        count=0
        rent=[]
        for document in result:
            sqft=document.get('RETAIL_SQUARE_FOOTAGE',0)
            pricePerSqft=document.get('PRICE_PER_SQ_FT',0)
            if sqft>0 and pricePerSqft>0:
                rent.append(round(pricePerSqft*sqft))
                # print("Rent:",rent[-1])
                count+=1
        if count==1:
            competitorRate={'builder':builder,'rent':rent[-1]}
        elif count>1:
            competitorRate={'builder':builder,'rent':round(sum(rent)/count,2)}
        if count>0:
            builderApiResponse.append(competitorRate)
    print(builderApiResponse)
    predictedRent=1000
    response={'average_competitor_rent':builderApiResponse}
    
    mongoClient.close()
    return response

@app.route('/rental/getPredictedRent', methods=['POST'])
def getPredictedRent():
    data=request.json
    addressDetails=getAddressDetails(data['address'])
    mlModelRequest={'CONDO_OR_RENTAL':data.get('condo_or_rental','Rental'),
                    'DISTRICT_REGION':data['region'] if 'region' in data else abort(400, description='region is not provided'),
                    'PARKING_TYPE':data.get('parking_type'),
                    'LAUNDRY_TYPE_PER_SUITE_TYPE':data.get('laundry'),
                    'CITY':data.get('city','Halifax'),
                    'BEDS':data['beds'] if 'beds' in data else abort(400, description='beds is not provided'),
                    'RETAIL_SQUARE_FOOTAGE':data['size_sqft'] if 'size_sqft' in data else abort(400, description='size_sqft is not provided'),
                    'PRICE_PER_SQ_FT':data['price_per_sqft'] if 'price_per_sqft' in data else abort(400, description='price_per_sqft is not provided'),
                    'TRANSIT_SCORE':addressDetails['transitScore'],
                    'LATITUDE':addressDetails['latitude'],
                    'LONGITUDE':addressDetails['longitude'],
                    'BATHS':data.get('baths',1),
                    'WALK_SCORE':addressDetails['walkScore'],
                    'NO_OF_UTILITIES':data['no_of_utilities'] if 'no_of_utilities' in data else abort(400, description='no_of_utilities is not provided'),
                    'NO_OF_AMENITIES':data['no_of_amenities'] if 'no_of_amenities' in data else abort(400, description='no_of_amenities is not provided')}
    # Loading the trained ML Model in clf
    with open('rental_price_model.pkl', 'rb') as file:
        clf = pickle.load(file)
    response={'predicted_rent':round(clf.predict(pd.DataFrame.from_dict([mlModelRequest]))[0],2)}
    return response

@app.errorhandler(400)
def handleBadRequest(error):
    response=jsonify({'error':error.description})
    response.status_code=error.code
    return response

if __name__=='__main__':
    app.run(debug=True)
