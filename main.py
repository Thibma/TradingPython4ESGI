import requests
import json
import csv
import os.path
import time
import base64
import hashlib
import hmac
import numpy as np
from datetime import datetime


apiKey = 'APIKEY'
apiSecret = base64.b64decode("APISECRET")

def getTimeStamp():
    url = "https://api.kraken.com/0/public/Time"

    r = requests.get(url)

    jsonReponse = r.json()

    time = datetime.utcfromtimestamp(jsonReponse["result"]["unixtime"]).strftime('%d/%m/%Y %H:%M:%S')
    #print(time)
    return time


def getAllAsset():
    url = "https://api.kraken.com/0/public/AssetPairs"

    r = requests.get(url)

    jsonReponse = r.json()
    jsonResult = jsonReponse["result"]

    tickersList = []

    for key, value in jsonResult.items():
        tickersList.append(key)

    print(tickersList)


def getPriceOfTicker(ticker):
    url = "https://api.kraken.com/0/public/Ticker?pair=" + ticker

    r = requests.get(url)
    jsonResponse = r.json()

    if not jsonResponse["error"]:
        value = jsonResponse["result"][ticker]["c"][0]
        #print(value)
        return value
    else:
        print("Paramètre incorrect")

def saveTickerBTCEUR():
    value = getPriceOfTicker("XXBTZEUR")
    timeStamp = getTimeStamp()
    dictOutput = ["XXBTZEUR", timeStamp, value]

    if os.path.isfile('ticker.csv') == False:
        with open('ticker.csv', 'w') as f:
            firstLine = ["Ticker", "Time", "Price"]
            writer = csv.writer(f)
            writer.writerow(firstLine)
            f.close()

    with open('ticker.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(dictOutput)
        f.close()
    
    logs = open('logs.txt', 'a')
    logs.write(timeStamp + " : Récupération du prix du ticker XXBTZEUR\n")
    logs.close()

def saveAverage():
    with open('ticker.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)

        prices = []

        for price in reader:
            prices.append(price[2])
        
        f.close()

    lastPrices = []
    for i in range (len(prices) - 5, len(prices)):
        lastPrices.append(float(prices[i]))

    average = sum(lastPrices) / len(lastPrices)

    if os.path.isfile('average.csv') == False:
        with open('average.csv', 'w') as f:
            firstLine = ["Time", "Average"]
            writer = csv.writer(f)
            writer.writerow(firstLine)
            f.close()

    with open('average.csv', 'a') as f:
        writer = csv.writer(f)
        timeStamp = getTimeStamp()
        data = [average, timeStamp]
        writer.writerow(data)
        f.close

    logs = open('logs.txt', 'a')
    logs.write(timeStamp + " : Sauvegarde de le moyenne des prix du ticker XXBTZEUR\n")
    logs.close()

def getBalanceAccount():
    api_path = "/0/private/Balance"
    api_nonce = str(int(time.time()*1000))
    api_post = "nonce=" + api_nonce

    # Cryptographic hash algorithms
    api_sha256 = hashlib.sha256(api_nonce.encode("utf-8") + api_post.encode("utf-8")).digest()
    api_hmac = hmac.new(apiSecret, (api_path + str(api_sha256)).encode("utf-8"), hashlib.sha512)

    # Encode signature into base64 format used in API-Sign value
    api_signature = base64.b64encode(api_hmac.digest())
    url = "https://api.kraken.com/0/private/Balance"

    headers = {
        'API-Key': apiKey,
        'API-Sign': api_signature
    }

    data = {
        'nonce': np.uint64(time.time()*1000)
    }

    print(headers)

    r = requests.post(url, data = data, headers = headers)

    print(r.json())

averageCounter = 0

#getBalanceAccount()

print("Bot en fonctionnement")

while 1:
    saveTickerBTCEUR()
    if averageCounter == 5:
        averageCounter = 0
        saveAverage()
    else:
        averageCounter += 1
    time.sleep(10)