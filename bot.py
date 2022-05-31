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
            sendMessage("Kullanıcı adınızı ve parolanızı arasında iki nokta olacak şekilde gonderiniz.\n\nÖrnek: kralali01:31mizAh31", id)
            while 1:
                id, text, date = getUpdate()
                gecici = text
                if ":" in text:
                    sendMessage(f"{text}  -->  Kullanıcı adın ve parolan doğru mu?(Doğruysa 'evet', değilse herhangi bir şey yazınız.)", id)
                    while 1:
                        id, text, date = getUpdate()
                        if text == "evet" or text == "Evet":
                            login = gecici
                            sendMessage("Oyunların ID'sini arasında virgül olacak şekilde yazınız.\n\nÖrnek:  730,302080,359550", id)
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
                                        sendMessage("Oyun ID'leri doğru değil.\n\nLütfen tekrar deneyiniz.", id)
                                        break
                                    with open("config", "w", encoding="UTF-8") as file:
                                        file.write(f"{login}\n{str(verified)}")
                                        date_list.append(date)
                                        sendMessage("Ayarlarınız başarıyla kaydedildi.", id)
                                    break
                            break
                        elif text!= gecici and text != "evet" and text != "Evet":
                            date_list.append(date)
                            sendMessage("Ayarlar kaydedilmeden çıkıldı.", id)
                            break    
                    break
                elif text != "/config" and ":" not in text and date not in date_list:
                    date_list.append(date)
                    sendMessage("Kullanıcı adınızı ve parolanızı arasında iki nokta olacak şekilde gonderiniz.\n\nÖrnek: kralali01:31mizAh31", id)
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
                    sendMessage("Steam Guard kodunu yazınız.", id)
                    while 1:
                        id, text, date = getUpdate()
                        if text != "/run":
                            date_list.append(date)
                            account_login = client.login(username=username, password=password, two_factor_code=text)
                            if str(account_login) == "EResult.InvalidPassword":
                                sendMessage("Yanlış parola!\n'/config' komutu ile parolanızı düzenleyin." , id)
                                break
                            elif str(account_login) == "EResult.OK":
                                sendMessage("Başarıyla giriş yaptınız. Oyunlar çalışıyor..", id)
                                client.games_played(oyunID)
                                client.run_forever()
                                break
                            elif str(account_login) == "EResult.TwoFactorCodeMismatch":
                                sendMessage('Yanlış guard kodu!\nYeniden deneyiniz.', id)
                                break
                elif str(account_login) == "EResult.AccountLogonDenied":
                    sendMessage("Mailinize gelen Steam Guard kodunu yazınız.", id)
                    while 1:
                        id, text, date = getUpdate()
                        if text != "/run":
                            date_list.append(date)
                            account_login = client.login(username=username, password=password, auth_code=text)
                            if str(account_login) == "EResult.InvalidPassword":
                                sendMessage("Yanlış parola!\n'/config' komutu ile parolanızı düzenleyin." , id)
                                break
                            elif str(account_login) == "EResult.OK":
                                sendMessage("Başarıyla giriş yaptınız. Oyunlar çalışıyor..", id)
                                client.games_played(oyunID)
                                client.run_forever()
                                break
                            elif str(account_login) == "EResult.InvalidLoginAuthCode":
                                sendMessage('Yanlış Guard kodu!\nYeniden deneyiniz.', id)
                                break
                elif str(account_login) == "EResult.InvalidPassword":
                    sendMessage("Yanlış parola!\n'/config' komutu ile parolanızı düzenleyin." , id)
                elif str(account_login) == "EResult.OK":
                    client.games_played(oyunID)
                    client.run_forever()
                else:
                    sendMessage("Hata: " + str(account_login), id)        
            except FileNotFoundError:
                sendMessage("'/config' komutunu kullanarak parolanızı ve kullanıcı adınızı yazınız.", id)  

        elif text == "/start" and date not in date_list:
            date_list.append(date)
            sendMessage("Merhaba,\nBu bot Steam'de bulunan oyunlarınızın saatini arttırır.\nNasıl kullanıldığını öğrenmek için '/help' yazınız.", id)
        
        elif text == "/help" and date not in date_list:
            date_list.append(date)
            sendMessage("/config --> Steam kullanıcı adı, parola ve saatini arttırmak istediğiniz oyunları kaydeder.\n\n/run --> Saat arttırma işlemine başlar.", id)
        
        elif text != "/config" and text != "/run" and text != "/start" and text != "/help" and date not in date_list:
            date_list.append(date)
            sendMessage("Yazdığınızı anlayamadım.\n\nKomutları görmek için '/help' yazınız.", id)
    except:
        pass
