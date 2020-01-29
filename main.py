import requests
import time
import json
import xlwt
import os
import platform
import sys
import tkinter as tk


wins = 0

def getSummonerID(summonerName, APIKey):#summonerv4
    URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    #print (URL)
    response = requests.get(URL)
    response = response.json()
    #print(response)
    #print("")
    return response["accountId"]

def getGameID(ID, APIKey):#matchv4 420 = ranked 400 = normal draft 700 = clash
    URL = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/"+ID+"?queue=" + "400" +"&api_key="+APIKey
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
            print(response["matches"][lastMatch - x])
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


def getScore(response, summonerName):
    global wins
    for x in range(0,10):
        if(response["participantIdentities"][x]["player"]["summonerName"]) == summonerName:
            playerNumber = x+1
    team = 0 if playerNumber <= 5 else  1

    score = 0
    gameTime = round(response["gameDuration"]/60,1) # in mins
    role = response["participants"][playerNumber-1]["timeline"]["lane"]

    #print(response["teams"][team])
    score += response["teams"][team]["baronKills"]/2
    if response["teams"][team]["firstDragon"]:
        score +=1
    if response["teams"][team]["dragonKills"] >= 4:
        score +=1
    #if response["teams"][team]["firstRiftHerald"] and role == "Top" or role == "Jungle":
        #score +=1
    #kda
    if response["participants"][playerNumber-1]["stats"]["deaths"] != 0:
        kda = (response["participants"][playerNumber-1]["stats"]["kills"] + response["participants"][playerNumber-1]["stats"]["assists"])/response["participants"][playerNumber-1]["stats"]["deaths"]
    else:
        kda = (response["participants"][playerNumber-1]["stats"]["kills"] + response["participants"][playerNumber-1]["stats"]["assists"])


    #wins
    if(response["participants"][playerNumber-1]["stats"]["win"]):
        score += 5
        wins +=1
    #killing spree
    if response["participants"][playerNumber-1]["stats"]["largestKillingSpree"] >= 7:
        score +=1
    #multiKill
    if response["participants"][playerNumber-1]["stats"]["largestMultiKill"] == 5:
        score += 2
    #dmg Per Min - champions
    if response["participants"][playerNumber-1]["stats"]["totalDamageDealtToChampions"]/gameTime >= 1000:
        score += 1
    #Dmg per min - objectives
    if response["participants"][playerNumber-1]["stats"]["damageDealtToObjectives"]/gameTime >= 500:
        score += 1
    #vision Score
    if response["participants"][playerNumber-1]["stats"]["visionScore"] >= 50:
        score +=1
        if role == "Support":
            score +=1.5
        if response["participants"][playerNumber-1]["stats"]["visionScore"] > 100:
            score += 1
    #crowd control score
    if response["participants"][playerNumber-1]["stats"]["timeCCingOthers"] >= 35:
        score += 1
        if role == "Support":
            score +=1.5
        if response["participants"][playerNumber-1]["stats"]["timeCCingOthers"] > 55:
            score += 1
    #healing
    if response["participants"][playerNumber-1]["stats"]["totalHeal"] >= 2500 and response["participants"][playerNumber-1]["stats"]["totalHeal"] >= 3:
        score += 1
        if role == "Support":
            score += 1.5
    #vision wards
    if response["participants"][playerNumber-1]["stats"]["visionWardsBoughtInGame"] >= 3:
        score +=1
    #wards placed
    if response["participants"][playerNumber-1]["stats"]["wardsPlaced"] >= 25:
        score +=1
    #wards killed
    if response["participants"][playerNumber-1]["stats"]["wardsKilled"] >= 20:
        score +=2
    #first blood
    if response["participants"][playerNumber-1]["stats"]["firstBloodKill"] or response["participants"][playerNumber-1]["stats"]["firstBloodAssist"] == True:
        score += 1
    #first tower
    if response["participants"][playerNumber-1]["stats"]["firstTowerKill"] or response["participants"][playerNumber-1]["stats"]["firstTowerAssist"] == True:
        score += 1

    count = 0
    #xp per min vs opponent
    for x in range(0,len(response["participants"][playerNumber-1]["timeline"]["xpDiffPerMinDeltas"])*10, 10):
        if response["participants"][playerNumber-1]["timeline"]["xpDiffPerMinDeltas"][str(x)+"-"+str(x+10)] > 0:
            count +=1
        else:
            count += -1
    if count > 0:
        score += 1

    #gold per min
    count = 0
    for x in range(0,len(response["participants"][playerNumber-1]["timeline"]["goldPerMinDeltas"])*10, 10):
        if response["participants"][playerNumber-1]["timeline"]["goldPerMinDeltas"][str(x)+"-"+str(x+10)] > 450 and role != "Support":
            count +=1
        else:
            count += -1
    if count > 0:
        score += 1

    #cs per min vs opponent
    count = 0
    for x in range(0,len(response["participants"][playerNumber-1]["timeline"]["csDiffPerMinDeltas"])*10, 10):
        if response["participants"][playerNumber-1]["timeline"]["csDiffPerMinDeltas"][str(x)+"-"+str(x+10)] > 0 and role != "Support":
            count +=1
        else:
            count += -1
    if count > 0:
        score += 1

    #cs per min
    count = 0
    for x in range(0,len(response["participants"][playerNumber-1]["timeline"]["creepsPerMinDeltas"])*10, 10):
        if response["participants"][playerNumber-1]["timeline"]["creepsPerMinDeltas"][str(x)+"-"+str(x+10)] > 6.5 and role != "Support":
            count +=1
    else:
        count += -1
    if count >0:
        score += 1

    #print(response["participants"][playerNumber-1])
    print(str(kda) + " as " + str(response["participants"][playerNumber-1]["championId"]))
    print("score as \"champion\" " + str(score))
    return score


def toSheet(score, score2, data, data2, summonerName, row, record, wb, sheet):



    style = xlwt.easyxf('align: horiz center; borders: left thin, right thin, top thin, bottom thin;')
    sheet.write(row,0, summonerName, style)
    sheet.write(row,1, record, style)
    sheet.write(row, 2, score+score2, style)

    wb.save("WebScraperResults.xls")
'''#champion and KDA
    sheet.write(row,3, firstKDA + " as " + firstChamp, style)
    sheet.write(row,10, secondKDA + " as " + secondChamp, style)
#mvp
    sheet.write(row,4, firstMVP , style)
    sheet.write(row,11, secondMVP , style)
#multi-kills
    sheet.write(row,5, firstMultiKill , style)
    sheet.write(row,12, secondMultiKill , style)
#KPA
    sheet.write(row,6, "KPA: " + firstKPA + "%", style)
    sheet.write(row,13, "KPA: " + secondKPA + "%", style)
#CS
    sheet.write(row,7, "CS per Min: "  + str(firstCS), style)
    sheet.write(row,14, "CS per Min: "  + str(secondCS), style)
#control wards
    sheet.write(row,8, "Control wards "  + str(firstCW), style)
    sheet.write(row,15, "Control wards " + str(secondCW), style)
#gameTime
    sheet.write(row,9, "Game Time:" + str(firstGameTime), style)
    sheet.write(row,16, "Game Time:" +  str(secondGameTime), style)'''




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

    def on_closing2():
        log.write("closing...")
        print("closing...")
        log.close()
        root2.destroy()

    def on_closing():
        print("closing...")
        root.destroy()
        sys.exit(0)

    #setting up GUI

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.configure(background='lightgrey')
    btn_text = tk.StringVar()
    weekNum = tk.StringVar()

    btn_text.set("Run")
    #player List and week number
    PlayerFile = tk.Text(root, width=45, height= 20)
    #weekNumber = tk.Text(root, width=10, height= 1)

    '''if(len(sys.argv) > 1 and ("-specific" in sys.argv[1] or "-s" in sys.argv[1])):
        with open("players.txt", 'r') as f:
            PlayerFile.insert(tk.END, f.read())
    else:'''
    with open("players.txt", 'r') as f:
        PlayerFile.insert(tk.END, f.read())

    #labels
    #if(len(sys.argv) > 1 and ("-specific" in sys.argv[1] or "-s" in sys.argv[1])):
    #    label = tk.Label(root, text = "The Players to be updated")
    #else:
    label = tk.Label(root, text = "The Players")
    #label2 = tk.Label(root, text = "Enter the week number: ")
    placeHolder = tk.Label(root, text = "   ")

    placeHolder.configure(background='lightgrey')
    #label2.configure(background='lightgrey')
    label.configure(background='lightgrey')
    #buttons
    setPlayers = tk.Button(root, text="Save Changes", command=saveChanges)
    btnRun = tk.Button(root, textvariable=btn_text, command=clear)

    label.pack()
    PlayerFile.pack(fill="none", expand=True)
    setPlayers.config(bg = 'lightgrey')
    #EditPlayers.pack()
    setPlayers.pack()
    #label2.pack(side=tk.LEFT)
    #weekNumber.pack(side=tk.LEFT)
    #placeHolder.pack(side = tk.LEFT)
    btnRun.pack()

    #weekNum = weekNumber.get("1.0",'end-1c')

    root.geometry("550x400+200+150")
    if(len(sys.argv) > 1 and ("-auto" in sys.argv[1] or "-a" in sys.argv[1])):
        root.destroy()

    root.mainloop()


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
    #summonerName = "ddibwynt"

        file = open("apikey.txt","r")
        APIKey = file.readline()
        file.close()
        


        ID  = getSummonerID(summonerName, APIKey)
        games = getGameID(ID, APIKey)
        #print("games are ")
        #print (games)
        #print(games[0])
        '''for x in range(0,3):
            print("---------------------------------------------------------------------------------------------------------------------------------------------------------")
        print("")'''
        if(games[0] != "DEFAULT"):
            data = getGameData(games[0], APIKey)
            score = getScore(data, summonerName)
        else:
            score = 0
            data = "NULL"

        if(games[1] != "DEFAULT"):
            data2 = getGameData(games[1], APIKey)
            score2 = getScore(data2, summonerName)
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
        os.system("webScraperResults.xls")
    else:
        os.system("open webScraperResults.xls")

    print("Program complete")


if __name__ == "__main__":
    main()
