import requests
import time
import json

def getSummonerID(summonerName, APIKey):#summonerv4
    URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    #print (URL)
    response = requests.get(URL)
    response = response.json()
    print(response)
    print("")
    return response["accountId"]

def getGameID(ID, APIKey):#matchv4 420 = ranked 400 = normal draft 700 = clash
    URL = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/"+ID+"?queue=" + "420" +"&api_key="+APIKey
    #print (URL)
    response = requests.get(URL)
    response = response.json()
    ts = round(time.time())
    gamesGrabbed = 0
    print("time is " + str(ts))
    lastMatch = len(response["matches"])
    for x in range (1,lastMatch):
        daysAgo = (ts - round(response["matches"][lastMatch - x]['timestamp']/1000))/(60*60*24)
        if(daysAgo <= 7):
            gamesGrabbed += 1
            print(response["matches"][lastMatch - x])
            print("")
            if(gamesGrabbed == 2):
                return [g1,response["matches"][lastMatch - x]["gameId"]]
            else:
                g1 = response["matches"][lastMatch - x]["gameId"]

def getGameData(gameID, APIKey, summonerName):
    URL = "https://na1.api.riotgames.com/lol/match/v4/matches/" + str(gameID) +"?api_key=" + APIKey
    response = requests.get(URL)
    response = response.json()
    for x in range(0,10):
        if(response["participantIdentities"][x]["player"]["summonerName"]) == summonerName:
            playerNumber = x+1
    team = 0 if playerNumber <= 5 else  1
    score = 0
    print(response["teams"][team])
    print(response["teams"][team]["baronKills"])
    print(response["teams"][team]["firstDragon"])
    print(response["teams"][team]["firstRiftHerald"])
    print(response["teams"][team]["dragonKills"])



    if(response["participants"][playerNumber-1]["stats"]["win"]):
        score += 5
    kda = (response["participants"][playerNumber-1]["stats"]["kills"] + response["participants"][playerNumber-1]["stats"]["assists"])/response["participants"][playerNumber-1]["stats"]["deaths"]
    print (kda)
    response["participants"][playerNumber-1]["timeline"]["lane"]
    print(response["participants"][playerNumber-1]["championId"])

    if response["participants"][playerNumber-1]["stats"]["largestKillingSpree"] >= 6:
        score +=1
    if response["participants"][playerNumber-1]["stats"]["largestMultiKill"] == 5:
        score += 2
    if response["participants"][playerNumber-1]["stats"]["totalDamageDealt"]:
        tmp = 0
    if response["participants"][playerNumber-1]["stats"]["damageDealtToObjectives"]:
        tmp = 0
    if response["participants"][playerNumber-1]["stats"]["visionScore"] >= 50:
        score +=2
    if response["participants"][playerNumber-1]["stats"]["timeCCingOthers"] >= 35:
        score += 2
    if response["participants"][playerNumber-1]["stats"]["totalHeal"] >= 2500 and response["participants"][playerNumber-1]["stats"]["totalHeal"] >= 3:
        score += 2
    if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= 3:
        score +=1
    if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= 12:
        score +=1
    if response["participants"][playerNumber-1]["stats"]["wardsKilled"] >= 20:
        score +=2
    if response["participants"][playerNumber-1]["stats"]["firstBloodKill"] or response["participants"][playerNumber-1]["stats"]["firstBloodAssist"] == True:
        score += 1
    if response["participants"][playerNumber-1]["stats"]["firstTowerKill"] or response["participants"][playerNumber-1]["stats"]["firstTowerAssist"] == True:
        score += 1


    for x in range(0,len(response["participants"][playerNumber-1]["timeline"]["xpDiffPerMinDeltas"])*10, 10):
        print(str(x)+"-"+str(x+10) + " " + str(response["participants"][playerNumber-1]["timeline"]["xpDiffPerMinDeltas"][str(x)+"-"+str(x+10)]))
        
    for x in range(0,len(response["participants"][playerNumber-1]["timeline"]["goldPerMinDeltas"])*10, 10):
        print(str(x)+"-"+str(x+10) + " " + str(response["participants"][playerNumber-1]["timeline"]["goldPerMinDeltas"][str(x)+"-"+str(x+10)]))

    for x in range(0,len(response["participants"][playerNumber-1]["timeline"]["csDiffPerMinDeltas"])*10, 10):
        print(str(x)+"-"+str(x+10) + " " + str(response["participants"][playerNumber-1]["timeline"]["csDiffPerMinDeltas"][str(x)+"-"+str(x+10)]))

    for x in range(0,len(response["participants"][playerNumber-1]["timeline"]["creepsPerMinDeltas"])*10, 10):
        print(str(x)+"-"+str(x+10) + " " + str(response["participants"][playerNumber-1]["timeline"]["creepsPerMinDeltas"][str(x)+"-"+str(x+10)]))


    print(response["participants"][playerNumber-1])


def main():

    summonerName = "ddibwynt"#(str)(input('Type your Summoner Name here '))
    APIKey = "RGAPI-4fe29b67-c543-423b-93fa-fb1db9d8e44a"

    ID  = getSummonerID(summonerName, APIKey)
    games= getGameID(ID, APIKey)
    print(games[0])
    for x in range(0,3):
        print("------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("")
    getGameData(games[0], APIKey, summonerName)

    #getGameData(games[1],APIKey)


if __name__ == "__main__":
    main()
