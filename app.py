import json
import datetime
import os
import time
from fugle_marketdata import RestClient

clientCode = ""
with open('code.txt', 'r') as file:
    # code.txt need put api key from fugle
    clientCode = file.read()
if clientCode == "":
    print("you need get api key from https://developer.fugle.tw/")
    print("than put api key in code.txt")
    print("input enter to exit program")
CLIENT = RestClient(api_key = clientCode)
STOCK = CLIENT.stock

def start():
    print("run stock check program")

    # read json
    stockJson = []
    with open('focus.json') as f:
        d = json.load(f)
        stockJson = d

    # Check stock has open
    # Get today
    today = datetime.datetime.today()
    todayMonth = today.month
    todayDay = today.day
    hasOpen = True
    sleepJson = []
    with open('sleep.json') as f:
        d = json.load(f)
        sleepJson = d
        for i in range(len(sleepJson)):
            pass
            if (str(todayMonth) + "_" + str(todayDay)) == sleepJson[i]["date"]:
                # stop program
                hasOpen = False
    if hasOpen == False:
        print("Today is not open stock")
        input("input enter to exit program")
        return True
    # check stockJson's date
    for i in reversed(range(len(stockJson))):
        if stockJson[i]["use_date"] != (str(todayMonth) + "_" + str(todayDay)):
            del stockJson[i]
            pass
    if stockJson == []:
        print("Today have not stock to check")
        input("input enter to exit program")
        return True
            
    # loading until am 9.
    loadingAndPrint(jsonData=stockJson)

def loadingAndPrint(jsonData):
    pass
    nowTime = time.localtime()
    tHour = nowTime.tm_hour
    while True:
        if int(tHour) >= 8:
            break
        else:
            time.sleep(1)
    # now time has over 9 am 
    # print date and focus stock
    print("date: {}".format(str(nowTime.tm_mon) + "_" + str(nowTime.tm_mday)))
    print("--------------------------------------------------------")
    stockString ="stock: "
    for i in range(len(jsonData)):
        pass
        stockString = stockString + str(jsonData[i]["stock"]) + ", "
    # check data after 5min
    while True:
        checkTime = time.localtime(time.time())
        if (((int(checkTime.tm_min)) % 5) == 0) and (checkTime.tm_hour < 10) and (checkTime.tm_sec == 10):
        # if True:
            # because sometime have error that client has been 50 min but stock server only 49 min
            # my get data will lost
        # if True:
            # check data
            callApiToCheck(jsonData, checkTime)
            time.sleep(60)
            pass
        elif (checkTime.tm_hour >= 10):
        # elif False:
            # stop check
            print("check time is over")
            input("input enter to exit program")
            return True
        time.sleep(1)

    
def callApiToCheck(jsonData, thisDay):
    print("now will check stock")
    stockList = []
    for i in range(len(jsonData)):
        if (str(thisDay.tm_mon) + "_" + str(thisDay.tm_mday)) == jsonData[i]["use_date"]:
            # check date is same time, because I afraid I will purchase error stock
            stockList.append(jsonData[i]["stock"])
    if len(stockList) >= 20:
        print("Your stock item too many, only 19 stock can check at the same time")
        return True
    elif stockList != []:
        # It mean today have stock to check, it will get data be api
        # get stock data, and put it in dict
        recallMessage = ""
        for i  in range(len(stockList)):
            stockCallQuote = STOCK.intraday.quote(symbol=str(jsonData[i]["stock"]))
            stockCallCandles = STOCK.intraday.candles(symbol=str(jsonData[i]["stock"]), timeframe = '1', sort = 'desc')
            # stockCallVolumes = STOCK.intraday.volumes(symbol=str(jsonData[i]["stock"]))
            # get yesterday data
            stockCallYesterday = STOCK.historical.candles(**{"symbol": str(jsonData[i]["stock"]),
                                                             "from": getPreviousDay(),
                                                             "to": getPreviousDay(),
                                                             "timeframe": "D"})
            stockApiDate = {"stock": str(jsonData[i]["stock"]),
                                 "previousClose": stockCallQuote["previousClose"],
                                 "openPrice": stockCallQuote["openPrice"],
                                 "lastPrice": stockCallQuote["lastTrade"]["price"],
                                 "fiveKdata": getFiveTimeData(stockCallCandles["data"]),
                                 "volume": {"volume": stockCallQuote["total"]["tradeVolume"],
                                            "atBid": stockCallQuote["total"]["tradeVolumeAtBid"],
                                            "atAsk": stockCallQuote["total"]["tradeVolumeAtAsk"]},
                                 "yesterdayData": stockCallYesterday["data"]
                                }
            
            if jsonData[i]["method"] == "many":
                # fiveKdate in api have delay, some date use 'lastTrade.price' instead
                # check today increase < 5%
                if float(stockApiDate["lastPrice"])/stockApiDate["previousClose"] >= 1.05:
                    # if true mean this price is more up and too quickly, maybe down soon
                    print(str(jsonData[i]["stock"]) + " has too high")
                    continue
                # last 5K data openPrice < previousClose
                if stockApiDate['fiveKdata'][0]['open'] >= stockApiDate["lastPrice"]:
                    # if true mean in this 5k, price is down
                    print(str(jsonData[i]["stock"]) + " price has down")
                    continue
                # buy over 60%
                # if not buyOverSixty(stockApiDate["volume"], "buy"):
                if not float(stockApiDate["volume"]["atAsk"])/(stockApiDate["volume"]["atAsk"] + stockApiDate["volume"]["atBid"]) > 0.6:
                    print(str(jsonData[i]["stock"]) + " power is not enough")
                    # if true mean power is not enough
                    continue
                # estimate over yesterday stock volume
                if not stockApiDate['volume']["volume"] > stockApiDate["yesterdayData"][0]["volume"]:
                    print(str(jsonData[i]["stock"]) + " volume is not more than estimate")
                    # if true mean volume is not enough
                    continue
                # last 5K previousClose > up_line
                if not (stockApiDate['previousClose'] > jsonData[i]["up_line"]):
                    print(str(jsonData[i]["stock"]) + " price is not more than up_line")
                    # if true mean now price is not high
                    continue
                if jsonData[i]["reload"] == "yes":
                    # last 5K openPrice > up_line
                    if not (stockApiDate['openPrice'] > jsonData[i]["up_line"]):
                        print(str(jsonData[i]["stock"]) + " openPrice is not more than up_line")
                        # if reload is true, openPrice need bigger than up_line
                        continue
                    pass
                elif jsonData[i]["reload"] == "no":
                    # last 5K openPrice > down_line
                    if not (stockApiDate['openPrice'] > jsonData[i]["down_line"]):
                        print(str(jsonData[i]["stock"]) + " openPrice is not more than down_line")
                        # if reload is true, openPrice need bigger than down_line
                        continue
                    pass
            elif jsonData[i]["method"] == "lost":
                # check today down < 5%
                if float(stockApiDate['fiveKdata'][0]["close"])/stockApiDate["previousClose"] <= 0.95:
                    # if true mean this price is down and too quickly, maybe up soon
                    print(str(jsonData[i]["stock"]) + " has too down")
                    continue
                # last 5K data openPrice > previousClose
                if stockApiDate['fiveKdata'][0]['open'] <= stockApiDate['fiveKdata'][0]['close']:
                    # if true mean in this 5k, price is up
                    print(str(jsonData[i]["stock"]) + " price has up")
                    continue
                # sell over 60%
                if not float(stockApiDate["volume"]["atBid"])/(stockApiDate["volume"]["atAsk"] + stockApiDate["volume"]["atBid"]) > 0.6:
                    # if true mean power is not enough
                    print(str(jsonData[i]["stock"]) + " power is not enough")
                    continue
                # last 5K previousClose < down_line
                if not (stockApiDate['previousClose'] < jsonData[i]["down_line"]):
                    print(str(jsonData[i]["stock"]) + " prevoousClose is not low enough")
                    # if true mean now price is not low
                    continue
                if jsonData[i]["reload"] == "yes":
                    # last 5K openPrice < down_line
                    if not (stockApiDate['openPrice'] < jsonData[i]["down_line"]):
                        print(str(jsonData[i]["stock"]) + " previousClose is not low enough")
                        # if reload is true, openPrice need bigger than down_line
                        continue
                    pass
                elif jsonData[i]["reload"] == "no":
                    # last 5K openPrice < up_line
                    if not (stockApiDate['openPrice'] < jsonData[i]["up_line"]):
                        print(str(jsonData[i]["stock"]) + " openPrice is too high")
                        # if reload is true, openPrice will bigger than up_line
                        continue
                    pass
            # if all item is ok, print it on terminal
            print("time" + str(thisDay.tm_mon) + "_" + str(thisDay.tm_mday) + " "
                    + str(thisDay.tm_hour) + "_" + str(thisDay.tm_min) + " "
                    + str(jsonData[i]["stock"]) + " "
                    + jsonData[i]["method"] + " chance")

        print("now all stock has check")
        pass
    elif stockList == []:
        print("have not stock need check")
    pass

def buyOverSixty(volume, buyOrSell):
    # check buy and sell %
    volumeAtAsk = 0
    volumeAtBid = 0
    for i in range(len(volume)):
        volumeAtBid = volumeAtBid + volume[i]['volumeAtBid']
        volumeAtAsk = volumeAtAsk + volume[i]['volumeAtAsk']
        pass
    if (float(volumeAtAsk)/(volumeAtAsk + volumeAtBid) > 0.6) and buyOrSell == "buy":
        return True
    elif (float(volumeAtBid)/(volumeAtAsk + volumeAtBid) > 0.6) and buyOrSell == "sell":
        return True
    else:
        # mean buy or sell power is not enough
        return False

def enoughEstimate(volume, yesterdayData, nowTime):
    # check today volume have more than yesterday volume
    todayVolume = 0
    nowEstimate = 0
    for i in range(len(volume)):
        todayVolume = todayVolume + volume[i]["volume"]
    yesterdayVolume = yesterdayData[0]["volume"]
    nowTimeHour = nowTime.tm_hour
    nowTimeMin = nowTime.tm_min
    if nowTimeHour == 9 and nowTimeMin <= 15:
        nowEstimate = todayVolume * 8
    elif nowTimeHour == 9 and nowTimeMin <= 30:
        nowEstimate = todayVolume * 5
    elif nowTimeHour == 9 and nowTimeMin <= 45:
        nowEstimate = todayVolume * 4
    elif nowTimeHour == 9 and nowTimeMin <= 60:
        nowEstimate = todayVolume * 3
    elif nowTimeHour == 10 and nowTimeMin <= 15:
        nowEstimate = todayVolume * 2.5
    elif nowTimeHour == 10 and nowTimeMin <= 30:
        nowEstimate = todayVolume * 2.2
    elif nowTimeHour == 10 and nowTimeMin <= 45:
        nowEstimate = todayVolume * 2
    elif nowTimeHour == 10 and nowTimeMin <= 60:
        nowEstimate = todayVolume * 1.8
    elif nowTimeHour == 11 and nowTimeMin <= 15:
        nowEstimate = todayVolume * 1.7
    elif nowTimeHour == 11 and nowTimeMin <= 30:
        nowEstimate = todayVolume * 1.6
    elif nowTimeHour == 11 and nowTimeMin <= 45:
        nowEstimate = todayVolume * 1.5
    elif nowTimeHour == 11 and nowTimeMin <= 60:
        nowEstimate = todayVolume * 1.45
    elif nowTimeHour == 12 and nowTimeMin <= 15:
        nowEstimate = todayVolume * 1.38
    elif nowTimeHour == 12 and nowTimeMin <= 30:
        nowEstimate = todayVolume * 1.32
    elif nowTimeHour == 12 and nowTimeMin <= 45:
        nowEstimate = todayVolume * 1.25
    elif nowTimeHour == 12 and nowTimeMin <= 60:
        nowEstimate = todayVolume * 1.18
    elif nowTimeHour == 13 and nowTimeMin <= 15:
        nowEstimate = todayVolume * 1.11
    elif nowTimeHour == 13 and nowTimeMin <= 30:
        nowEstimate = todayVolume * 1

    if nowEstimate > yesterdayVolume:
        return True
    else:
        return False

def getPreviousDay():
    if 0 < int(datetime.datetime.weekday(datetime.datetime.today())) < 6:
        return str(datetime.date.today() + datetime.timedelta(-1))
    elif int(datetime.datetime.weekday(datetime.datetime.today())) == 0:
        return str(datetime.date.today() + datetime.timedelta(-3))
    elif int(datetime.datetime.weekday(datetime.datetime.today())) == 6:
        return str(datetime.date.today() + datetime.timedelta(-2))
    pass

def getFiveTimeData(candols):
    if len(candols) % 5 == 0:
        kTimes = 5
    else:
        kTimes = len(candols) % 5
    FiveTimesOpen = 0
    FiveTimesHigh = 0
    FiveTimesLow = 99990
    FiveTimesClose = 0
    for i in range(kTimes):
        if i == 0:
            FiveTimesClose = candols[i]["close"]
        if i == kTimes - 1:
            FiveTimesOpen = candols[i]["open"]
        if FiveTimesHigh < candols[i]["high"]:
            FiveTimesHigh = candols[i]["high"]
        if FiveTimesLow > candols[i]["low"]:
            FiveTimesLow = candols[i]["low"]
    pass
    return [{"open": FiveTimesOpen, "close": FiveTimesClose, "high": FiveTimesHigh, "low": FiveTimesLow}]


if __name__ ==  "__main__":
    start()