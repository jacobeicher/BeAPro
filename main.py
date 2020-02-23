import requests
import pymongo
import time
import json
import xlwt
import os
import platform
import sys
import tkinter as tk


wins = 0

LOW = 'low'
MID = 'med'
HIGH = 'high'

scoring = {
    'low': {'dragonSoul': 0, 'baronKills': .5, 'wardScore': 50, 'wardScoreExtra': 100, 'controlWards': 4, 'controlWardsExtra': 6, 'wardsPlaced': 15,
            'wardsPlacedExtra': 25, 'wardsKilled': 20, 'wardsKilledExtra': 25, 'kda': 3.5, 'kdaExtra': 4.5, 'killingSpree': 7,
            'dmgPerMinChampions': 1000, 'dmgPerMinObjectives': 500, 'crowdcontrolScore': 35, 'crowdcontrolScoreExtra': 55, 'healing': 2500,
            'expPerMinVsOpp': 400, 'csPerMinVsOpp': 6.5, 'goldPerMinVsOpp': 450},

    'lowPoints': {'dragonSoul': 1, 'baronKills': .5, 'wardScore': 1, 'wardScoreExtra': 2, 'controlWards': 1, 'controlWardsExtra': 2, 'wardsPlaced': 1,
                  'wardsPlacedExtra': 1.5, 'wardsKilled': 1.5, 'wardsKilledExtra': 2, 'firstBlood': 1, 'firstTower': 1, 'kda': 1, 'kdaExtra': 2, 'killingSpree': 2,
                  'pentakill': 5, 'dmgPerMinChampions': 1, 'dmgPerMinObjectives': 1, 'crowdcontrolScore': 1, 'crowdcontrolScoreExtra': 1, 'healing': 1,
                  'expPerMinVsOpp': 1, 'csPerMinVsOpp': 2, 'goldPerMinVsOpp': 1, 'win': 5},

    'med': {'dragonSoul': 0, 'baronKills': 0, 'wardScore': 0, 'wardScoreExtra': 0, 'controlWards': 0, 'controlWardsExtra': 0, 'wardsPlaced': 0,
            'wardsPlacedExtra': 0, 'wardsKilled': 0, 'wardsKilledExtra': 0, 'kda': 0, 'kdaExtra': 0, 'killingSpree': 0,
            'dmgPerMinChampions': 0, 'dmgPerMinObjectives': 0, 'crowdcontrolScore': 0, 'crowdcontrolScoreExtra': 0, 'healing': 0,
            'expPerMinVsOpp': 0, 'csPerMinVsOpp': 0, 'goldPerMinVsOpp': 0},

    'medPoints': {'dragonSoul': 0, 'baronKills': 0, 'wardScore': 0, 'wardScoreExtra': 0, 'controlWards': 0, 'controlWardsExtra': 0, 'wardsPlaced': 0,
                  'wardsPlacedExtra': 0, 'wardsKilled': 0, 'wardsKilledExtra': 0, 'firstBlood': 0, 'firstTower': 0, 'kda': 0, 'kdaExtra': 0, 'killingSpree': 0,
                  'pentakill': 0, 'dmgPerMinChampions': 0, 'dmgPerMinObjectives': 0, 'crowdcontrolScore': 0, 'crowdcontrolScoreExtra': 0, 'healing': 0,
                  'expPerMinVsOpp': 0, 'csPerMinVsOpp': 0, 'goldPerMinVsOpp': 0, 'win': 5},

    'high': {'dragonSoul': 0, 'baronKills': 0, 'wardScore': 50, 'wardScoreExtra': 4, 'controlWards': 7, 'controlWardsExtra': 0, 'wardsPlaced': 15,
             'wardsPlacedExtra': 25, 'wardsKilled': 20, 'wardsKilledExtra': 30, 'kda': 3.5, 'kdaExtra': 4.5, 'killingSpree': 0,
             'dmgPerMinChampions': 1150, 'dmgPerMinObjectives': 500, 'crowdcontrolScore': 35, 'crowdcontrolScoreExtra': 55, 'healing': 2500,
             'expPerMinVsOpp': 450, 'csPerMinVsOpp': 7.5, 'goldPerMinVsOpp': 450},

    'highPoints': {'dragonSoul': 0, 'baronKills': 0, 'wardScore': 1, 'wardScoreExtra': 1, 'controlWards': 1, 'controlWardsExtra': 2, 'wardsPlaced': 1,
                   'wardsPlacedExtra': 2, 'wardsKilled': 1, 'wardsKilledExtra': 1, 'firstBlood': 2.5, 'firstTower': 1, 'kda': 1.5, 'kdaExtra': 3, 'killingSpree': 2,
                   'pentakill': 3, 'dmgPerMinChampions': 2, 'dmgPerMinObjectives': 0, 'crowdcontrolScore': 1, 'crowdcontrolScoreExtra': 1, 'healing': 1,
                   'expPerMinVsOpp': 1, 'csPerMinVsOpp': 2, 'goldPerMinVsOpp': 1, 'win': 5}
}


def getRank(summonerID, APIKey):  # league-V4
    URL = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + \
        summonerID + "?api_key=" + APIKey
    response = requests.get(URL)
    response = response.json()

    global LOW
    global MID
    global HIGH

    try:
        if response[0]['tier'] == "IRON" or response[0]['tier'] == "BRONZE" or response[0]['tier'] == "SILVER":
            return LOW
        elif response[0]['tier'] == "GOLD" or response[0]['tier'] == "PLATINUM":
            return MID
        else:
            return HIGH
    except:
        return LOW


def getSummonerID(summonerName, APIKey):  # summonerv4
    URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + \
        summonerName + "?api_key=" + APIKey
    #print (URL)
    response = requests.get(URL)
    response = response.json()
    # print(response)
    # print("")
    try:
        return [response["accountId"], response["id"]]
    except:
        print(response)
        sys.exit()


def getGameID(ID, APIKey):  # matchv4 420 = ranked, 400 = normal draft, 700 = clash
    URL = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/" + \
        ID+"?queue=" + "420" + "&api_key="+APIKey
    #print (URL)
    response = requests.get(URL)
    response = response.json()
    ts = round(time.time())
    gamesGrabbed = 0
    #print("time is " + str(ts))
    lastMatch = response["endIndex"]
    for x in range(1, lastMatch+1):
        daysAgo = (
            ts - round(response["matches"][lastMatch - x]['timestamp']/1000))/(60*60*24)
        if(daysAgo <= 7):
            gamesGrabbed += 1
            #(response["matches"][lastMatch - x])
            print("")
            if(gamesGrabbed == 2):
                return [g1, response["matches"][lastMatch - x]["gameId"]]
            else:
                g1 = response["matches"][lastMatch - x]["gameId"]
    if gamesGrabbed == 1:
        return [g1, "DEFAULT"]
    else:
        return ["DEFAULT", "DEFAULT"]


def getGameData(gameID, APIKey):
    URL = "https://na1.api.riotgames.com/lol/match/v4/matches/" + \
        str(gameID) + "?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()


def getScore(response, summonerName, rank):
    global wins
    global LOW
    global MID
    global HIGH

    # print(response)
    for x in range(0, 10):
        if(response["participantIdentities"][x]["player"]["summonerName"].lower()) == summonerName.lower():
            playerNumber = x+1
    team = 0 if playerNumber <= 5 else 1

    score = 0
    gameTime = round(response["gameDuration"]/60, 1)  # in mins
    role = response["participants"][playerNumber-1]["timeline"]["lane"]
    if role == "BOTTOM":
        if response["participants"][playerNumber-1]["timeline"]["role"] == "DOU_SUPPORT":
            role = "Support"
        else:
            role = "ADC"
    elif role == "NONE":
        role = "Jungle"
    # print(response["participants"][playerNumber-1])

    # print(response["teams"][team])
    if response["teams"][team]["baronKills"] >= scoring[rank]['baronKills']:
        score += scoring[rank+"Points"]['baronKills']

    # kda
    if response["participants"][playerNumber-1]["stats"]["deaths"] != 0:
        kda = (response["participants"][playerNumber-1]["stats"]["kills"] + response["participants"]
               [playerNumber-1]["stats"]["assists"])/response["participants"][playerNumber-1]["stats"]["deaths"]
    else:
        kda = (response["participants"][playerNumber-1]["stats"]["kills"] +
               response["participants"][playerNumber-1]["stats"]["assists"])
        score += 1

    if kda >= scoring[rank]['kda']:
        score += scoring[rank+'Points']['kda']
        if kda >= scoring[rank]['kdaExtra']:
            score += scoring[rank+'Points']['kdaExtra']

    # wins
    if(response["participants"][playerNumber-1]["stats"]["win"]):
        score += scoring[rank+"Points"]['win']
        wins += 1
    # killing spree
    if response["participants"][playerNumber-1]["stats"]["largestKillingSpree"] >= scoring[rank]['killingSpree']:
        score += scoring[rank+'Points']['killingSpree']
    # multiKill
    if response["participants"][playerNumber-1]["stats"]["largestMultiKill"] == 5:
        score += scoring[rank+'Points']['pentakill']
    # dmg Per Min - champions
    if response["participants"][playerNumber-1]["stats"]["totalDamageDealtToChampions"]/gameTime >= scoring[rank]['dmgPerMinChampions']:
        score += scoring[rank+'Points']['dmgPerMinChampions']

    # Dmg per min - objectives
    if response["participants"][playerNumber-1]["stats"]["totalDamageDealtToChampions"]/gameTime >= scoring[rank]['dmgPerMinObjectives']:
        score += scoring[rank+'Points']['dmgPerMinObjectives']
    # vision Score
    if response["participants"][playerNumber-1]["stats"]["visionScore"] >= scoring[rank]['wardScore']:
        score += scoring[rank+'Points']['wardScore']
        if role == "Support":
            score += 1.5
        if response["participants"][playerNumber-1]["stats"]["visionScore"] > scoring[rank]['wardScoreExtra'] and role == "Support":
            score += scoring[rank+'Points']['wardScoreExtra']
    # crowd control score
    if response["participants"][playerNumber-1]["stats"]["timeCCingOthers"] >= scoring[rank]['crowdcontrolScore']:
        score += scoring[rank+"Points"]['crowdcontrolScore']
        if response["participants"][playerNumber-1]["stats"]["timeCCingOthers"] > scoring[rank]['crowdcontrolScoreExtra']:
            score += scoring[rank+"Points"]['crowdcontrolScoreExtra']
    # healing
    if response["participants"][playerNumber-1]["stats"]["totalHeal"] >= scoring[rank]['healing'] and role == "Support":
        score += scoring[rank+"Points"]['healing']
    # control wards
    if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= scoring[rank]['controlWards']:
        score += scoring[rank+"Points"]['controlWards']
        if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= scoring[rank]['controlWardsExtra']:
            score += scoring[rank+"Points"]['controlWardsExtra']
    # wards placed

    if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= scoring[rank]['wardsPlaced']:
        score += scoring[rank+"Points"]['wardsPlaced']
        if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= scoring[rank]['wardsPlacedExtra']:
            score += scoring[rank+"Points"]['wardsPlacedExtra']
    # wards killed
    if response["participants"][playerNumber-1]["stats"]["wardsKilled"] >= scoring[rank]['wardsKilled']:
        score += scoring[rank+"Points"]['wardsKilled']
        if role == "Support" and response["participants"][playerNumber-1]["stats"]["wardsKilled"] >= scoring[rank]['wardsKilledExtra']:
            score += scoring[rank+"Points"]['wardsKilledExtra']
    # first blood
    if response["participants"][playerNumber-1]["stats"]["firstBloodKill"] or response["participants"][playerNumber-1]["stats"]["firstBloodAssist"] == True:
        score += scoring[rank+"Points"]['firstBlood']
    # first tower
    try:
        if response["participants"][playerNumber-1]["stats"]["firstTowerKill"] or response["participants"][playerNumber-1]["stats"]["firstTowerAssist"] == True:
            score += scoring[rank+"Points"]['firstTower']

    except:
        print("no towers taken")
        count = 0

    # xp per min vs opponent
    try:
        for x in range(0, round(gameTime-gameTime % 10), 10):
            if response["participants"][playerNumber-1]["timeline"]["xpDiffPerMinDeltas"][str(x)+"-"+str(x+10)] > 0:
                score += scoring[rank+"Points"]['expPerMinVsOpp']
                print(response["participants"][playerNumber-1]["timeline"]
                      ["xpDiffPerMinDeltas"][str(x)+"-"+str(x+10)])
            # else:
            #     count += -1
            #     print(response["participants"][playerNumber-1]["timeline"]["xpDiffPerMinDeltas"][str(x)+"-"+str(x+10)])
            # if count > 0:
            #     score += 1
            #     print("1 point earned for xp per min vs opp ")
    except:
        print("no xp per min")
        # xp per min
        count = 0
        try:
            for x in range(0, round(gameTime-gameTime % 10), 10):
                if response["participants"][playerNumber-1]["timeline"]["xpPerMinDeltas"][str(x)+"-"+str(x+10)] >= 450 and role != "Support":
                    score += scoring[rank+"Points"]['expPerMinVsOpp']

        except:
            print("no xp per min data")
    # gold per min
    count = 0
    try:
        for x in range(0, round(gameTime-gameTime % 10), 10):
            if response["participants"][playerNumber-1]["timeline"]["goldPerMinDeltas"][str(x)+"-"+str(x+10)] > 450 and role != "Support":
                score += scoring[rank+"Points"]['goldPerMinVsOpp']
        #     else:
        #         count += -1
        # if count > 0:
        #     score += 1
    except:
        print("no gold per min data")
    # cs per min vs opponent
    count = 0
    try:
        for x in range(0, round(gameTime-gameTime % 10), 10):
            if response["participants"][playerNumber-1]["timeline"]["csDiffPerMinDeltas"][str(x)+"-"+str(x+10)] > 0 and role != "Support":
                count += 1
                response["participants"][playerNumber -
                                         1]["timeline"]["csDiffPerMinDeltas"][str(x)+"-"+str(x+10)]
            else:
                count += -1
                response["participants"][playerNumber -
                                         1]["timeline"]["csDiffPerMinDeltas"][str(x)+"-"+str(x+10)]
        if count > 0:
            score += scoring[rank+"Points"]['csPerMinVsOpp']
            print("2 points earned for cs per min vs opp ")
    except:
        print("no CS per min vs opp")
        # cs per min
        count = 0
        try:
            for x in range(0, round(gameTime-gameTime % 10), 10):
                if response["participants"][playerNumber-1]["timeline"]["creepsPerMinDeltas"][str(x)+"-"+str(x+10)] > 6.5 and role != "Support":
                    score += scoring[rank+"Points"]['csPerMinVsOpp']

        except:
            print("no cs per min data")
    # print(response["participants"][playerNumber-1])
    print(str(kda) + " as " +
          str(response["participants"][playerNumber-1]["championId"]))
    print("score as \"champion\" " + str(score))
    return score


def toSheet(score, score2, data, data2, summonerName, row, record, wb, sheet):

    style = xlwt.easyxf(
        'align: horiz center; borders: left thin, right thin, top thin, bottom thin;')
    sheet.write(row, 0, summonerName, style)
    sheet.write(row, 1, record, style)
    sheet.write(row, 2, score+score2, style)

    wb.save("Results.xls")


def main():
    def clear():
        btnRun['highlightbackground'] = 'blue'
        root.after(200, reset_color)
        root.destroy()

    def reset_color():
        setPlayers['highlightbackground'] = 'white'
        btnRun['highlightbackground'] = 'white'

    def saveChanges():
        setPlayers['highlightbackground'] = 'blue'
        root.after(200, reset_color)

        input = PlayerFile.get("1.0", 'end-1c')
        if(len(sys.argv) > 1 and ("-specific" in sys.argv[1] or "-s" in sys.argv[1])):
            f = open("sPlayers.txt", "w+")
            f.write(input)
        else:
            f = open("players.txt", "w+")
            f.write(input)
        f.close()

    def on_closing():
        print("closing...")
        root.destroy()
        sys.exit(0)

    # setting up GUI

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.configure(background='lightgrey')
    btn_text = tk.StringVar()

    btn_text.set("Run")
    # player List
    PlayerFile = tk.Text(root, width=45, height=20)

    with open("players.txt", 'r') as f:
        PlayerFile.insert(tk.END, f.read())

    # labels
    label = tk.Label(root, text="The Players")

    placeHolder = tk.Label(root, text="   ")

    placeHolder.configure(background='lightgrey')

    label.configure(background='lightgrey')
    # buttons
    setPlayers = tk.Button(root, text="Save Changes", command=saveChanges)
    btnRun = tk.Button(root, textvariable=btn_text, command=clear)

    label.pack()
    PlayerFile.pack(fill="none", expand=True)
    setPlayers.config(bg='lightgrey')
    setPlayers.pack()
    btnRun.pack()

    root.geometry("550x400+200+150")
    if(len(sys.argv) > 1 and ("-auto" in sys.argv[1] or "-a" in sys.argv[1])):
        root.destroy()

    root.mainloop()

    # GUI end

    os.getenv("QUERY_STRING")
    managerID = sys.stdin.read()

    client = pymongo.MongoClient('mongodb+srv://admin:m7KZRsbDojGGb1H5@be-a-pro-db-yw0no.gcp.mongodb.net/test?retryWrites=true&w=majority')
    db = client['be-a-pro-db']
    array = list(db.users.find())     
    names = []

    for x in array:
        if x['managerId'] == managerID:
            names.append(x['ign'])
            

    row = 0
    #file = open("players.txt", "r")
    #names = file.readlines()
    #file.close()
    print(names)
    global wins

    wb = xlwt.Workbook()
    sheet = wb.add_sheet("sheet1")  # formatting sheet
    for i in range(0, 17):
        sheet.col(i).width = 256*30

    while(len(names) > 0):
        summonerName = names.pop(0).strip()
        print(summonerName + " is current player")

        file = open("apikey.txt", "r")
        APIKey = file.read()
        file.close()

        ids = getSummonerID(summonerName, APIKey)

        accountID = ids[0]
        summonerID = ids[1]
        rank = getRank(summonerID, APIKey)
        games = getGameID(accountID, APIKey)

        if(games[0] != "DEFAULT"):
            data = getGameData(games[0], APIKey)
            score = getScore(data, summonerName, rank)
        else:
            score = 0
            data = "NULL"

        if(games[1] != "DEFAULT"):
            data2 = getGameData(games[1], APIKey)
            score2 = getScore(data2, summonerName, rank)
        else:
            score2 = 0
            data2 = "NULL"

        if wins == 2:
            record = ("2,0")
        elif wins == 1:
            record = ("1,1")
        else:
            record = ("0,2")

        toSheet(score, score2, data, data2,
                summonerName, row, record, wb, sheet)
        row += 1
        wins = 0

    if(platform.system() == "Windows"):
        os.system("Results.xls")
    else:
        os.system("pwd")
        os.system("open Results.xls")

    print("Program complete")


if __name__ == "__main__":
    main()
