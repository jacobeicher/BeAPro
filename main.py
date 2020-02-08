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
    if response[0]['tier'] == "IRON" or response[0]['tier'] == "BRONZE" or response[0]['tier'] == "SILVER" or response[0]['tier'] == "GOLD":
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

def getGameID(ID, APIKey):#matchv4 420 = ranked, 400 = normal draft, 700 = clash
    URL = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/"+ID+"?queue=" + "420" +"&api_key="+APIKey
    #print (URL)
    response = requests.get(URL)
    response = response.json()
    ts = round(time.time())
    gamesGrabbed = 0
    #print("time is " + str(ts))
    lastMatch = response["endIndex"]
    for x in range (1,lastMatch+1):
        daysAgo = (ts - round(response["matches"][lastMatch - x]['timestamp']/1000))/(60*60*24)
        if(daysAgo <= 7):
            gamesGrabbed += 1
            #(response["matches"][lastMatch - x])
            print("")
            if(gamesGrabbed == 2):
                return [g1,response["matches"][lastMatch - x]["gameId"]]
            else:
                g1 = response["matches"][lastMatch - x]["gameId"]
    if gamesGrabbed == 1:
        return [g1,"DEFAULT"]
    else:
        return ["DEFAULT","DEFAULT"]

def getGameData(gameID, APIKey):
    URL = "https://na1.api.riotgames.com/lol/match/v4/matches/" + str(gameID) +"?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()


def getScore(response, summonerName, rank):
    global wins
    global LOW
    global HIGH
    #print(response)
    for x in range(0,10):
        if(response["participantIdentities"][x]["player"]["summonerName"].lower()) == summonerName.lower():
            playerNumber = x+1
    team = 0 if playerNumber <= 5 else  1

    score = 0
    gameTime = round(response["gameDuration"]/60,1) # in mins
    role = response["participants"][playerNumber-1]["timeline"]["lane"]

    print(response["participants"][playerNumber-1])

    #print(response["teams"][team])
    if rank == LOW:
        score += response["teams"][team]["baronKills"]/2

            
    #kda
    if response["participants"][playerNumber-1]["stats"]["deaths"] != 0:
        kda = (response["participants"][playerNumber-1]["stats"]["kills"] + response["participants"][playerNumber-1]["stats"]["assists"])/response["participants"][playerNumber-1]["stats"]["deaths"]
    else:
        kda = (response["participants"][playerNumber-1]["stats"]["kills"] + response["participants"][playerNumber-1]["stats"]["assists"])
        if rank == LOW:
            score +=1
    if rank == LOW:
        if kda >= 3.5:
            score +=1 
            if kda >= 4.5:
                score +=2
    elif rank == HIGH:
        if kda >= 3.5:
            score +=1.5 
            if kda >= 4.5:
                score +=3
    #wins
    if(response["participants"][playerNumber-1]["stats"]["win"]):
        score += 5
        wins +=1
    #killing spree
    if response["participants"][playerNumber-1]["stats"]["largestKillingSpree"] >= 7 and rank == low or response["participants"][playerNumber-1]["stats"]["largestKillingSpree"] >= 8 and rank == HIGH:
        score +=1
    #multiKill
    if response["participants"][playerNumber-1]["stats"]["largestMultiKill"] == 5:
        score += 5
    #dmg Per Min - champions
    if rank == LOW
        if response["participants"][playerNumber-1]["stats"]["totalDamageDealtToChampions"]/gameTime >= 1000:
            score += 1
    if rank == HIGH:
        if response["participants"][playerNumber-1]["stats"]["totalDamageDealtToChampions"]/gameTime >= 1150:
            score += 2
    #Dmg per min - objectives
    if response["participants"][playerNumber-1]["stats"]["damageDealtToObjectives"]/gameTime >= 500:
        if rank == LOW:
            score += 1
    #vision Score
    if response["participants"][playerNumber-1]["stats"]["visionScore"] >= 50:
        score +=1
        if role == "Support":
            score +=1.5
        if response["participants"][playerNumber-1]["stats"]["visionScore"] > 100 and role == "Support":
            score += 1
    #crowd control score
    if response["participants"][playerNumber-1]["stats"]["timeCCingOthers"] >= 35:
        score += 1
        if role == "Support":
            score +=1.5
        if response["participants"][playerNumber-1]["stats"]["timeCCingOthers"] > 55:
            score += 1
            if role == "Support":
                score +=1
    #healing
    if response["participants"][playerNumber-1]["stats"]["totalHeal"] >= 2500 and role == "Support":
            score +=1:
    #control wards
    if rank == LOW:
        if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= 4:
            score +=1
            if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= 6:
                score += 2
    if rank == HIGH:
        if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= 4:
            score +=1
            if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= 7:
                score += 2
    #wards placed
    
    if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= 15:
        score +=1
    if rank == LOW:
        if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= 25:
            score +=1.5
    if rank == HIGH:
        if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= 25:
            score +=2
    #wards killed
    if response["participants"][playerNumber-1]["stats"]["wardsKilled"] >= 20:
        if rank == LOW:
            score +=2
        if rank == HIGH:
            score +=1 
        if role == "Support" and response["participants"][playerNumber-1]["stats"]["wardsKilled"] >= 25:
            score +=1
    #first blood
    if response["participants"][playerNumber-1]["stats"]["firstBloodKill"] or response["participants"][playerNumber-1]["stats"]["firstBloodAssist"] == True:
        score += 1
        if rank == HIGH:
            score += 1.5
    #first tower
    try:
        if response["participants"][playerNumber-1]["stats"]["firstTowerKill"] or response["participants"][playerNumber-1]["stats"]["firstTowerAssist"] == True:
            score += 1

    except:
        print("no towers taken")


        count = 0

    #xp per min vs opponent
    try:
        for x in range(0,round(gameTime-gameTime%10), 10):
            if response["participants"][playerNumber-1]["timeline"]["xpDiffPerMinDeltas"][str(x)+"-"+str(x+10)] > 0:
                count +=1
            else:
                count += -1
            if count > 0:
                score += 1
    except:
        print("no xp per min data")
    #gold per min
    count = 0
    try:
        for x in range(0,round(gameTime-gameTime%10), 10):
            if response["participants"][playerNumber-1]["timeline"]["goldPerMinDeltas"][str(x)+"-"+str(x+10)] > 450 and role != "Support":
                count +=1
            else:
                count += -1
        if count > 0:
            score += 1
    except:
        print("no gold per min data")
    #cs per min vs opponent
    count = 0
    try:
        for x in range(0,round(gameTime-gameTime%10), 10):
            if response["participants"][playerNumber-1]["timeline"]["csDiffPerMinDeltas"][str(x)+"-"+str(x+10)] > 0 and role != "Support":
                count +=1
            else:
                count += -1
        if count > 0:
            score += 2
    except:
        print("no cs vs opp per min data")
    # #cs per min
    # count = 0
    # try:
    #     for x in range(0,round(gameTime-gameTime%10), 10):
    #         if response["participants"][playerNumber-1]["timeline"]["creepsPerMinDeltas"][str(x)+"-"+str(x+10)] > 6.5 and role != "Support":
    #             score +=1

    # except:
        # print("no cs per min data")
    #print(response["participants"][playerNumber-1])
    print(str(kda) + " as " + str(response["participants"][playerNumber-1]["championId"]))
    print("score as \"champion\" " + str(score))
    return score


def toSheet(score, score2, data, data2, summonerName, row, record, wb, sheet):



    style = xlwt.easyxf('align: horiz center; borders: left thin, right thin, top thin, bottom thin;')
    sheet.write(row,0, summonerName, style)
    sheet.write(row,1, record, style)
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

        input = PlayerFile.get("1.0",'end-1c')
        if(len(sys.argv) > 1 and ("-specific" in sys.argv[1] or "-s" in sys.argv[1])):
            f= open("sPlayers.txt","w+")
            f.write(input)
        else:
            f= open("players.txt","w+")
            f.write(input)
        f.close()

    def on_closing():
        print("closing...")
        root.destroy()
        sys.exit(0)

    #setting up GUI

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.configure(background='lightgrey')
    btn_text = tk.StringVar()

    btn_text.set("Run")
    #player List
    PlayerFile = tk.Text(root, width=45, height= 20)

    with open("players.txt", 'r') as f:
        PlayerFile.insert(tk.END, f.read())

    #labels
    label = tk.Label(root, text = "The Players")

    placeHolder = tk.Label(root, text = "   ")

    placeHolder.configure(background='lightgrey')

    label.configure(background='lightgrey')
    #buttons
    setPlayers = tk.Button(root, text="Save Changes", command=saveChanges)
    btnRun = tk.Button(root, textvariable=btn_text, command=clear)

    label.pack()
    PlayerFile.pack(fill="none", expand=True)
    setPlayers.config(bg = 'lightgrey')
    setPlayers.pack()
    btnRun.pack()


    root.geometry("550x400+200+150")
    if(len(sys.argv) > 1 and ("-auto" in sys.argv[1] or "-a" in sys.argv[1])):
        root.destroy()

    root.mainloop()

    # GUI end

    row =0
    file = open("players.txt","r")
    names = file.readlines()
    file.close()
    global wins

    wb = xlwt.Workbook()
    sheet = wb.add_sheet("sheet1")#formatting sheet
    for i in range(0, 17):
        sheet.col(i).width = 256*30

    while(len(names) > 0):
        summonerName = names.pop(0).strip()
        print(summonerName + " is current player")

        file = open("apikey.txt","r")
        APIKey = file.read()
        file.close()

        ids = getSummonerID(summonerName, APIKey)

        accountID  = ids[0]
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
            record =("1,1")
        else:
            record = ("0,2")

        toSheet(score, score2, data, data2, summonerName, row, record, wb, sheet)
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
