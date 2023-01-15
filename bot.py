from steam.client import SteamClient
import requests
# from threading import Thread
from os import environ

token = environ.get("TOKEN")
client = SteamClient()

def getUpdate():
    url = 'https://api.telegram.org/bot{}/getUpdates'.format(token)
    r = requests.get(url)
    x = 0
    while 1 :
        try:
            r.json()["result"][x]
            x+=1
        except IndexError:
            return (r.json()["result"][x-1]["message"]["chat"]["id"]), r.json()["result"][x-1]["message"]["text"], (r.json()["result"][x-1]["message"]["date"])

def sendMessage(text, id):
    requests.get(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={id}&text=" + text, timeout=3)
    
# def boost():
#     client.games_played(oyunID)
#     client.run_forever()

date_list = []
while 1:
    try:
        id, text, date = getUpdate()
    
        if text == "/config" and date not in date_list:
            date_list.append(date)
            sendMessage("Please enter your username and password with a colon between them.\n\nExample: kralali01:31mizAh31", id)
            while 1:
                id, text, date = getUpdate()
                gecici = text
                if ":" in text:
                    sendMessage(f"{text}  -->  Is the username and password correct? (If yes, type 'yes', if not, press 'enter')", id)
                    while 1:
                        id, text, date = getUpdate()
                        if text == "yes" or text == "Yes":
                            login = gecici
                            sendMessage("Please enter the ID's of the games separated by commas.\n\nExample: 730,302080,359550", id)
                            while 1:
                                id, text, date = getUpdate()
                                if "," in text:
                                    verified = []
                                    for i in text.split(","):
                                        verify = requests.get(f"https://store.steampowered.com/api/appdetails/?appids={i}&filters=basic").json()
                                        if verify == "null":
                                            pass
                                        elif verify[str(i)]["success"] == False:
                                            pass
                                        else:
                                            game_name = str(verify[str(i)]["data"]["name"])
                                            verified.append(int(i))
                                    if verified == []:
                                        sendMessage("The game IDs are incorrect. Please try again.", id)
                                        break
                                    with open("config", "w", encoding="UTF-8") as file:
                                        file.write(f"{login}\n{str(verified)}")
                                        date_list.append(date)
                                        sendMessage("Your settings have been saved successfully.", id)
                                    break
                            break
                        elif text!= gecici and text != "yes" and text != "Yes":
                            date_list.append(date)
                            sendMessage("Settings were not saved.", id)
                            break    
                    break
                elif text != "/config" and ":" not in text and date not in date_list:
                    date_list.append(date)
                    sendMessage("Please enter your username and password with a colon between them.\n\nExample: kralali01:31mizAh31", id)
                    break
                
        elif text == "/run" and date not in date_list:    
            date_list.append(date)
            try:
                with open("config", "r", encoding="UTF-8") as file:
                    login = file.readline().split("\n")[0]
                    oyunID = file.readline().strip('][').split(', ')
                username = login.split(":")[0]
                password = login.split(":")[1]
                account_login = client.login(username=username, password=password)
                if str(account_login) == "EResult.AccountLoginDeniedNeedTwoFactor":
                    sendMessage("Please enter your Steam Guard code.", id)
                    while 1:
                        id, text, date = getUpdate()
                        if text != "/run":
                            date_list.append(date)
                            account_login = client.login(username=username, password=password, two_factor_code=text)
                            if str(account_login) == "EResult.InvalidPassword":
                                sendMessage("Wrong password!\nEdit your password with the '/config' command." , id)
                                break
                            elif str(account_login) == "EResult.OK":
                                sendMessage("You have successfully logged in. Games are running.", id)
                                client.games_played(oyunID)
                                client.run_forever()
                                break
                            elif str(account_login) == "EResult.TwoFactorCodeMismatch":
                                sendMessage('Incorrect guard code!\nPlease try again.', id)
                                break
                elif str(account_login) == "EResult.AccountLogonDenied":
                    sendMessage("Please enter the Steam Guard code sent to your email.", id)
                    while 1:
                        id, text, date = getUpdate()
                        if text != "/run":
                            date_list.append(date)
                            account_login = client.login(username=username, password=password, auth_code=text)
                            if str(account_login) == "EResult.InvalidPassword":
                                sendMessage("Wrong password!\nEdit your password with the '/config' command." , id)
                                break
                            elif str(account_login) == "EResult.OK":
                                sendMessage("You have successfully logged in. Games are running..", id)
                                client.games_played(oyunID)
                                client.run_forever()
                                break
                            elif str(account_login) == "EResult.InvalidLoginAuthCode":
                                sendMessage('Incorrect guard code!\nPlease try again.', id)
                                break
                elif str(account_login) == "EResult.InvalidPassword":
                    sendMessage("Wrong password!\nEdit your password with the '/config' command." , id)
                elif str(account_login) == "EResult.OK":
                    client.games_played(oyunID)
                    client.run_forever()
                else:
                    sendMessage("Hata: " + str(account_login), id)        
            except FileNotFoundError:
                sendMessage("Enter your username and password by using the '/config' command.", id)  

        elif text == "/start" and date not in date_list:
            date_list.append(date)
            sendMessage("Hello,\nThis bot increases the hours played of games on Steam.\nType '/help' to learn how to use it.", id)
        
        elif text == "/help" and date not in date_list:
            date_list.append(date)
            sendMessage("/config --> Saves your Steam username, password, and the games you want to increase hours played.\n\n/run --> Begins the process of increasing hours played.", id)
        
        elif text != "/config" and text != "/run" and text != "/start" and text != "/help" and date not in date_list:
            date_list.append(date)
            sendMessage("I did not understand what you wrote.\n\nType '/help' to see the commands.", id)
    except:
        pass
