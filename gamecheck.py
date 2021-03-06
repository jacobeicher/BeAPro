import requests
import time
import json
import xlwt
import os
import platform
import sys
import tkinter as tk


wins = 0
LOW = 0
HIGH = 1

def getRank(summonerID, APIKey):#league-V4
    URL = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + summonerID+ "?api_key=" + APIKey
    response = requests.get(URL)
    response = response.json()
    global LOW
    global HIGH
    try:
        if response[0]['tier'] == "IRON" or response[0]['tier'] == "BRONZE" or response[0]['tier'] == "SILVER" or response[0]['tier'] == "GOLD":
            return LOW
    except:
        return LOW
    
    return HIGH

def getSummonerID(summonerName, APIKey):#summonerv4
    URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    #print (URL)
    response = requests.get(URL)
    response = response.json()
    #print(response)
    #print("")
    try:
        return [response["accountId"],response["id"]]
    except:
        print(response)
        sys.exit()

def getGameID(ID, APIKey, offSet):#matchv4 420 = ranked, 400 = normal draft, 700 = clash
    URL = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/"+ID+"?queue=" + "420" +"&api_key="+APIKey
    #print (URL)
    response = requests.get(URL)
    response = response.json()
    return [response["matches"][offSet]["gameId"],"DEFAULT"]

def getGameData(gameID, APIKey):#match v4
    URL = "https://na1.api.riotgames.com/lol/match/v4/matches/" + str(gameID) +"?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()

def getGameTimeline(gameID, APIKey):#match v4-timeline
    URL = "https://na1.api.riotgames.com/lol/match/v4/timelines/by-match/" + str(gameID) +"?api_key=" + APIKey
    response = requests.get(URL)
    print(response.json())

def getScore(response, summonerName, rank):
    global wins
    global LOW
    global HIGH
    for x in range(0,10):
        if(response["participantIdentities"][x]["player"]["summonerName"].lower()) == summonerName.lower():
            playerNumber = x+1
    team = 0 if playerNumber <= 5 else  1

    score = 0
    print(response["participants"][playerNumber-1]["timeline"])
    gameTime = round(response["gameDuration"]/60,1) # in mins
    role = response["participants"][playerNumber-1]["timeline"]["lane"]
    if role == "BOTTOM":
        if (response["participants"][playerNumber-1]["timeline"]["role"] == "SOLO" or response["participants"][playerNumber-1]["timeline"]["role"] == "DOU_SUPPORT") and response["participants"][playerNumber-1]["stats"]["totalMinionsKilled"]/gameTime < 3:
            role = "Support"
        else:
            role = "ADC"
    elif role == "NONE":
        role ="Jungle"
    #print(response["participants"][playerNumber-1])
    
    print(role)
    print("rank is " +  str(rank))
    #print(response["teams"][team])
    if rank == LOW:
        score += response["teams"][team]["baronKills"]/2
        print(str(score) + " points earned for barons")

            
    #kda
    if response["participants"][playerNumber-1]["stats"]["deaths"] != 0:
        kda = (response["participants"][playerNumber-1]["stats"]["kills"] + response["participants"][playerNumber-1]["stats"]["assists"])/response["participants"][playerNumber-1]["stats"]["deaths"]
    else:
        kda = (response["participants"][playerNumber-1]["stats"]["kills"] + response["participants"][playerNumber-1]["stats"]["assists"])
        if rank == LOW:
            score +=1
            print("1 point earned for no deaths")
    if rank == LOW:
        if kda >= 3.5:
            score +=1 
            print("1 point earned for kda > 3.5")
            if kda >= 4.5:
                score +=2
                print("2 points earned for kda > 4.5 ")
    elif rank == HIGH:
        if kda >= 3.5:
            score +=1.5 
            print("1.5 point earned for kda > 3.5")
            if kda >= 4.5:
                score +=3
                print("3 points earned for kda > 4.5 ")
    #wins
    if(response["participants"][playerNumber-1]["stats"]["win"]):
        score += 5
        wins +=1
        print("5 points earned for win ")
    #killing spree
    if response["participants"][playerNumber-1]["stats"]["largestKillingSpree"] >= 7 and rank == LOW or response["participants"][playerNumber-1]["stats"]["largestKillingSpree"] >= 8 and rank == HIGH:
        score +=1
        print("1 point earned for killing spree")
    #multiKill
    if response["participants"][playerNumber-1]["stats"]["largestMultiKill"] == 5:
        score += 5
        print("5 point earned for penta kill")
    #dmg Per Min - champions
    if rank == LOW:
        if response["participants"][playerNumber-1]["stats"]["totalDamageDealtToChampions"]/gameTime >= 1000:
            score += 1
            print("1 point earned for dmg per to champs")
    if rank == HIGH:
        if response["participants"][playerNumber-1]["stats"]["totalDamageDealtToChampions"]/gameTime >= 1150:
            score += 2
            print("2 point earned for dmg per to champs")
    #Dmg per min - objectives
    if response["participants"][playerNumber-1]["stats"]["damageDealtToObjectives"]/gameTime >= 500:
        if rank == LOW:
            score += 1
            print("1 point earned for dmg per min to objectives")
    #vision Score
    if response["participants"][playerNumber-1]["stats"]["visionScore"] >= 50:
        score +=1
        print("1 point earned for vision score")
        if role == "Support":
            score +=1.5
            print("1.5 support points earned for  vision score")
        if response["participants"][playerNumber-1]["stats"]["visionScore"] > 100 and role == "Support":
            score += 1
            print("1 support point earned for big vison score")
    #crowd control score
    if response["participants"][playerNumber-1]["stats"]["timeCCingOthers"] >= 35:
        score += 1
        print("1 point earned for cc score")
        if response["participants"][playerNumber-1]["stats"]["timeCCingOthers"] > 55:
            score += 1
            print("1 point earned for big cc score ")
    #healing    
    if response["participants"][playerNumber-1]["stats"]["totalHeal"] >= 2500 and role == "Support":
            score +=1
            print("1 point earned for heaing allies")
    #control wards
    if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= 4:
        score +=1
        print("1 point earned for buying 4 control wards")

    if rank == LOW:
        if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= 6:
            score += 2
            print("2 point earned for buying 6 vision wards")
    if rank == HIGH:
        if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= 7:
            score += 2
            print("2 point earned for buying 7 vision wards")
    #wards placed
    
    if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= 15:
        score +=1
        print("1 point earned for placing 15 wards ")
    if rank == LOW:
        if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= 25:
            score +=1.5
            print("1.5 points earned for placing 25 wards")
    if rank == HIGH:
        if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= 25:
            score +=2
            print("2 points earned for placing 25 wards")
    #wards killed
    if response["participants"][playerNumber-1]["stats"]["wardsKilled"] >= 20:
        if rank == LOW:
            score +=2
            print("2 points earned for killing wards")
        if rank == HIGH:
            score +=1 
            print("1 point earned for killing 25 wards")
        if role == "Support" and response["participants"][playerNumber-1]["stats"]["wardsKilled"] >= 25:
            score +=1
            print("1 support point earned for killing 25 wards")
    #first blood
    
    if response["participants"][playerNumber-1]["stats"]["firstBloodKill"] or response["participants"][playerNumber-1]["stats"]["firstBloodAssist"]:
        if rank == LOW:
            score += 1
            print("1 point earned for first blood")
        if rank == HIGH:
            score += 1.5
            print("1.5 point earned for first blood")
    #first tower
    try:
        if response["participants"][playerNumber-1]["stats"]["firstTowerKill"] or response["participants"][playerNumber-1]["stats"]["firstTowerAssist"] == True:
            score += 1
            print("1 point earned for first tower")

    except:
        print("no towers taken")


        count = 0

    #xp per min vs opponent

    print(response["participants"][playerNumber-1]["timeline"])

    try:
        for x in range(0,round(gameTime-gameTime%10), 10):
            if response["participants"][playerNumber-1]["timeline"]["xpDiffPerMinDeltas"][str(x)+"-"+str(x+10)] > 0:
                score +=1
                print("1 point for xp per min vs opp")
            # else:
            #     count += -1
            #     print(response["participants"][playerNumber-1]["timeline"]["xpDiffPerMinDeltas"][str(x)+"-"+str(x+10)])
            # if count > 0:
            #     score += 1
            #     print("1 point earned for xp per min vs opp ")
    except:
        print("no xp per min")
        #xp per min
        count = 0
        try:
            for x in range(0,round(gameTime-gameTime%10), 10):
                if response["participants"][playerNumber-1]["timeline"]["xpPerMinDeltas"][str(x)+"-"+str(x+10)] >= 450:
                    score +=1
                    print("1 point for xp per min")

        except:
            print("no xp per min data")
    #gold per min
    count = 0
    try:
        for x in range(0,round(gameTime-gameTime%10), 10):
            if response["participants"][playerNumber-1]["timeline"]["goldPerMinDeltas"][str(x)+"-"+str(x+10)] > 425 and role != "Support":
                score +=1
                print(response["participants"][playerNumber-1]["timeline"]["goldPerMinDeltas"][str(x)+"-"+str(x+10)])
            # else:
            #     count += -1
            #     print(response["participants"][playerNumber-1]["timeline"]["goldPerMinDeltas"][str(x)+"-"+str(x+10)])
        #if count > 0:
            #score += 1
            #print("1 point earned for gold per min ")
    except:
        print('no gold per min')
    #cs per min vs opponent
    count = 0
    try:
        for x in range(0,round(gameTime-gameTime%10), 10):
            if response["participants"][playerNumber-1]["timeline"]["csDiffPerMinDeltas"][str(x)+"-"+str(x+10)] > 0 and role != "Support":
                count +=1
                response["participants"][playerNumber-1]["timeline"]["csDiffPerMinDeltas"][str(x)+"-"+str(x+10)]
            else:
                count += -1
                response["participants"][playerNumber-1]["timeline"]["csDiffPerMinDeltas"][str(x)+"-"+str(x+10)]
        if count > 0:
            score += 2
            print("2 points earned for cs per min vs opp ")
    except:
        print("no CS per min vs opp")
        #cs per min
        count = 0
        try:
            for x in range(0,round(gameTime-gameTime%10), 10):
                if response["participants"][playerNumber-1]["timeline"]["creepsPerMinDeltas"][str(x)+"-"+str(x+10)] >= 6.5 and role != "Support":
                    score +=1
                    print("1 point for cs per min")

        except:
            print("no cs per min data")
     
           
    #print(response["participants"][playerNumber-1])
    #print(str(kda) + " as " + str(response["participants"][playerNumber-1]["championId"]))
    #print("score as \"champion\" " + str(score))
    return score


def main():

    global wins

    print("Enter player name")
    summonerName = input()
    summonerName = summonerName.strip()

    print("which game do you want? (1 for most recent game, 2 ect)")
    offSet = input()

    if offSet.find('-') >= 0:
        start = int(offSet[0:offSet.find('-')])
        end = int(offSet[offSet.find('-')+1:])
    else:
        start = int(offSet)
        end = int(offSet)
    
    for x in range(start, end+1):
        print(summonerName + " is current player")

        file = open("apikey.txt","r")
        APIKey = file.read()
        file.close()

        ids = getSummonerID(summonerName, APIKey)

        accountID  = ids[0]
        summonerID = ids[1]
        rank = getRank(summonerID, APIKey)
        games = getGameID(accountID, APIKey, int(x) - 1)

        print(games[0])
    
        data = getGameData(games[0], APIKey)
        score = getScore(data, summonerName, rank)


        print("score is " + str(score))

    #print("Program complete")


if __name__ == "__main__":
    main()
