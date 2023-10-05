from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.chrome.options import Options
import string
import random
import datetime
import csv
import os
import colorama
import keyboard
from colorama import Fore
colorama.init(autoreset=True)

# WARNING: MUST HAVE THE SAME SETTINGS!!!!!!


def date():
    Date = datetime.date.today()
    Date = Date.strftime("%m/%d/%Y")
    return Date

def generate_id(keys):
    while True:
        N = 10
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        key = str(key)
        if key not in keys:
            keys.add(key)
            break
    return key

def launchBrowser(url):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_experimental_option("detach", True)
    # options.add_argument('--window-size=1920,1080')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    options.add_argument('log-level=3')
    driver.get(url)
    return driver

def buy_indicator(MA_indicator, V_indicator, SQZ_indicator, price, middle_line):
    trend = float(MA_indicator["fast_ma"].text) > float(MA_indicator["slow_ma"].text) and float(price.text) > float(middle_line.text)
    volume = float(V_indicator["total_volume"].text) > float(V_indicator["volume_ma"].text) and float(V_indicator["volume"].text) > 70 and float(V_indicator["a_volume"].text) > 70 and V_indicator["volume"].get_attribute("style")[10:-1] == "(0, 137, 123)" and V_indicator["a_volume"].get_attribute("style")[10:-1] == "(76, 175, 80)"
    squeeze = SQZ_indicator["squeeze_status"].get_attribute("style")[10:-1] == "(120, 123, 134)"
    momentum = SQZ_indicator["momentum"].get_attribute("style")[10:-1] == "(0, 255, 0)"
    if trend and volume and not squeeze and momentum:
        return True
    else:
        return False

def sell_indicator(MA_indicator, V_indicator, SQZ_indicator, price, middle_line):
    trend = float(MA_indicator["fast_ma"].text) < float(MA_indicator["slow_ma"].text) and float(price.text) < float(middle_line.text)
    volume = float(V_indicator["total_volume"].text) > float(V_indicator["volume_ma"].text) and float(V_indicator["volume"].text) > 70 and float(V_indicator["a_volume"].text) > 70 and V_indicator["volume"].get_attribute("style")[10:-1] == "(136, 14, 79)" and V_indicator["a_volume"].get_attribute("style")[10:-1] == "(255, 82, 82)"
    squeeze = SQZ_indicator["squeeze_status"].get_attribute("style")[10:-1] == "(120, 123, 134)"
    momentum = SQZ_indicator["momentum"].get_attribute("style")[10:-1] == "(255, 0, 0)"
    if trend and volume and not squeeze and momentum:
        return True
    else:
        return False

def enter_long_position(price, balance, trades, position, keys, Asset, support, decimal, atr):
    p = float(price.text)
    quantity = balance / p
    stop_loss = float(support.text)
    pull_back = float(atr.text)
    fib_0 = (p - 0.382*stop_loss) / 0.618
    take_profit = fib_0 + (fib_0 - stop_loss)*0.618
    stop_loss -= pull_back
    take_profit -= pull_back
    stop_loss = round(stop_loss, decimal)
    take_profit = round(take_profit, decimal)
    t = Time.text[:-8]
    balance -= p*quantity
    trade_id = generate_id(keys)
    trades[trade_id] = {"id": trade_id, "Asset": Asset, "position": "long", "quantity": quantity, "stop-loss": stop_loss, "take-profit": take_profit,"entry price": round(p,decimal), "exit price": 0.0,"entry date": str(Date), "exit date": "", "entry time": t, "exit time" : "" ,"profit": 0.0, "balance": balance}
    position = trade_id
    return (balance, trades, position, keys)

def enter_short_position(price, balance, trades, position, keys, Asset, resistance, decimal, atr):
    p = float(price.text)
    quantity = balance / p
    stop_loss = float(resistance.text)
    pull_back = float(atr.text)
    fib_0 = (p - 0.382*stop_loss) / 0.618
    take_profit = fib_0 + (fib_0 - stop_loss)*0.618
    stop_loss += pull_back
    take_profit += pull_back
    stop_loss = round(stop_loss, decimal)
    take_profit = round(take_profit, decimal)
    balance += p*quantity
    trade_id = generate_id(keys)
    Date = date()
    t=Time.text[:-8]
    trades[trade_id] = {"id": trade_id, "Asset": Asset, "position": "short", "quantity": quantity, "stop-loss": stop_loss, "take-profit": take_profit,"entry price": round(p,decimal), "exit price": 0.0,"entry date": str(Date), "exit date": "", "entry time": t, "exit time" : "" ,"profit": 0.0, "balance": balance}
    position = trade_id
    return (balance, trades, position, keys)

def exit_long_position(price, Time, profit, balance, trades,position):
    p = float(price.text)
    t = Time.text[:-8]
    Date = date()
    trades[position]["exit date"] = str(Date)
    profit += (p-trades[position]["entry price"])*trades[position]["quantity"]
    balance += p*trades[position]["quantity"]
    trades[position]["exit price"] = round(p,decimal)
    trades[position]["profit"] = round((p-trades[position]["entry price"])*trades[position]["quantity"],decimal)
    trades[position]["exit time"] = t
    trades[position]["balance"] = balance
    return (balance, profit, trades)

def exit_short_position(price, Time, profit, balance, trades,position):
    p = float(price.text)
    t = Time.text[:-8]
    Date = date()
    trades[position]["exit date"] = str(Date)
    profit += (trades[position]["entry price"]-p)*trades[position]["quantity"]
    balance -= p*trades[position]["quantity"]
    trades[position]["exit price"] = round(p,decimal)
    trades[position]["profit"] = round((trades[position]["entry price"]-p)*trades[position]["quantity"],decimal)
    trades[position]["exit time"] = t
    trades[position]["balance"] = balance
    return (balance, profit, trades)


def running(curr, dur):
    # remember to check whether all trades are sold
    hour = (int(curr[:2]) + dur) % 24
    if hour < 10:
        hour = "0" + str(hour)
    stopTime = str(hour) + curr[2:]
    return stopTime

def real_time_sleep(second):
    while second > 0:
        if Time.text[:-8][3:] == "59:59":
            while Time.text[:-8][3:] == "59:59":
                pass
            second -= 1
        else:
            t = (int(Time.text[:-8][3:-3])*60 + int(Time.text[:-8][6:]) + second)
            while t - (int(Time.text[:-8][3:-3])*60 + int(Time.text[:-8][6:])) > 0:
                pass
            second -= 1
    return 1


def generate_id(keys):
    while True:
        N = 10
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        key = str(key)
        if key not in keys:
            keys.add(key)
            break
    return key


if __name__ == "__main__":
    disable_user_interaction_script = """
        var elementList = document.getElementsByTagName("*");
        for (var i = 0; i < elementList.length; i++) {
            elementList[i].style.pointerEvents = "none";
        }
    """
    enable_user_interaction_script = """
        var elementList = document.getElementsByTagName("*");
        for (var i = 0; i < elementList.length; i++) {
            elementList[i].style.pointerEvents = "auto";
        }
    """
    Date = date()
    MA_indicator = {}
    DC_indicator ={}
    V_indicator = {}
    SQZ_indicator = {}
    # WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"")))
    try:
        tradingview = launchBrowser("https://www.tradingview.com/accounts/signin/")
        WebDriverWait(tradingview, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Email']"))).click()
        WebDriverWait(tradingview, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"id_username\"]"))).send_keys("username")
        tradingview.find_element(By.XPATH, "//*[@id=\"id_password\"]").send_keys("password" + Keys.RETURN)
        input("Press Enter to continue")
        os.system('cls' if os.name == 'nt' else 'clear') # clear the console
        print(Fore.RED + "Starting the bot...")
        tradingview.refresh()

        tradingview.get('https://www.tradingview.com/chart/i5VACUPZ/?symbol=BINANCE%3ABTCUSD')
        price = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[2]/div/div[5]/div[2]")))
        highest_price = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[2]/div/div[3]/div[2]")))
        lowest_price = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/div[1]/div[1]/div[2]/div/div[4]/div[2]")))
        MA_indicator["fast_ma"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div")))
        MA_indicator["slow_ma"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/div[2]/div[2]/div[2]/div[2]/div/div[1]/div")))
        DC_indicator["support"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[3]/div")))
        DC_indicator["resistance"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[2]/div")))
        DC_indicator["middle_line"] =  WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/div[2]/div[2]/div[3]/div[2]/div/div[1]/div")))
        V_indicator["volume"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[1]/div")))
        V_indicator["a_volume"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[2]/div")))
        V_indicator["total_volume"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[3]/div")))
        V_indicator["volume_ma"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[3]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[6]/div")))
        SQZ_indicator["squeeze_status"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[5]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[2]/div")))
        SQZ_indicator["momentum"] = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[5]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/div[1]/div")))
        atr = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[5]/div[2]/div[1]/div/div[2]/div[7]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/div/div/div")))
        market_status = WebDriverWait(tradingview, 10).until(EC.presence_of_element_located((By.XPATH,"/html/body/div[2]/div[6]/div/div[2]/div[1]/div[1]/div[2]/div[2]/div/div[2]/div[3]/div/span[2]")))
        decimal = float(price.text)
        decimal = len(str(decimal).split('.')[-1])
        title=WebDriverWait(tradingview, 10).until(EC.presence_of_all_elements_located((By.XPATH, "/html/head/title")))
        Asset = title[0].get_attribute("text").split(" ")
        Asset = Asset[0]
        Time = tradingview.find_element(By.XPATH, "/html/body/div[2]/div[5]/div[1]/div/div[3]/div[1]/div/button/div")
        balance = 10000
        trades = {}
        position = ""
        keys = set()
        profit = 0
        Date = date()
        current_Trend = ""
        long = False
        short = False
    except:
        print(Fore.RED + "Failed to start the bot. Please try again.")
        tradingview.close()
        tradingview.quit()


    if float(MA_indicator["fast_ma"].text) > float(MA_indicator["slow_ma"].text):
        current_Trend = Fore.GREEN + "bullish"
    elif float(MA_indicator["fast_ma"].text) < float(MA_indicator["slow_ma"].text):
        current_Trend = Fore.RED + "bearish"
    else:
        current_Trend = Fore.RED + "no trend"
    squeeze = SQZ_indicator["squeeze_status"].get_attribute("style")[10:-1] == "(120, 123, 134)"
    flag = True
    # tradingview.execute_script(disable_user_interaction_script)

    while True:
        try:
            reconnect = tradingview.find_element(By.XPATH, '//*[@id="overlap-manager-root"]/div[2]/div/div[2]/div/div/div[1]/div[2]/div/button')
            print(Fore.RED + "Reconnecting")
            print()
            # tradingview.execute_script(enable_user_interaction_script)
            reconnect.click()
            # tradingview.execute_script(disable_user_interaction_script)
        except:
            pass
        try:
            real_time_sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear') # clear the console
            if (len(trades) != 0 and position != ""):
                print(trades[position])
            if float(MA_indicator["fast_ma"].text) < float(MA_indicator["slow_ma"].text) and (current_Trend == Fore.GREEN + "bullish" or current_Trend == "no trend"):
                current_Trend = Fore.RED + "bearish"
            elif float(MA_indicator["fast_ma"].text) > float(MA_indicator["slow_ma"].text) and (current_Trend == Fore.RED + "bearish" or current_Trend == "no trend"):
                current_Trend = Fore.GREEN + "bullish"
            elif float(MA_indicator["fast_ma"].text) == float(MA_indicator["slow_ma"].text):
                current_Trend = "no trend"
            squeeze = SQZ_indicator["squeeze_status"].get_attribute("style")[10:-1] == "(120, 123, 134)"
            print("Current Trend:", current_Trend)
            print("Asset:", Asset)
            print("Balance:",balance)
            print("Profit:", profit)
            print("Price:", price.text)
            print(Time.text[:-8])
            print("Market Status:", market_status.text)
            if squeeze:
                flag = False
            if flag:
                continue
            if long:
                if float(lowest_price.text) <= trades[position]["stop-loss"] or float(highest_price.text) >= trades[position]["take-profit"]:
                    if not squeeze:
                        flag = True
                    balance, profit, trades = exit_long_position(price, Time, profit, balance, trades,position)
                    position = ""
                    long = False
            elif short:
                if float(highest_price.text) >= trades[position]["stop-loss"] or float(lowest_price.text) <= trades[position]["take-profit"]:
                    if not squeeze:
                        flag = True
                    balance, profit, trades = exit_short_position(price, Time, profit, balance, trades,position)
                    position = ""
                    short = False
            if position == "" and current_Trend == Fore.GREEN + "bullish" and buy_indicator(MA_indicator, V_indicator, SQZ_indicator, price, DC_indicator["middle_line"]) and market_status.text != "MARKET CLOSED":
                balance, trades, position, keys = enter_long_position(price, balance, trades, position, keys, Asset, DC_indicator["support"], decimal, atr)
                long = True
            elif position == "" and current_Trend == Fore.RED + "bearish" and sell_indicator(MA_indicator, V_indicator, SQZ_indicator, price, DC_indicator["middle_line"]) and market_status.text != "MARKET CLOSED":
                balance, trades, position, keys = enter_short_position(price, balance, trades, position, keys, Asset, DC_indicator["resistance"], decimal, atr)
                short = True
        except KeyboardInterrupt:
            if position == "":
                break
            else:
                tmp = '-1'
                while tmp != '1' and tmp != '2':
                    tmp = input("Currently in a position. Press 1 to quit or 2 to continue.")
                if tmp == '1':
                    break
                elif tmp == '2':
                    continue
        except:
            continue


    print("Trades:", trades)
    print("Total profit:", profit)
    print("Balance:", balance)
    Date = date()
    Date = Date.replace("/","-")
    filename = "./data/"+"data_"+Date+".csv"
    exist = os.path.exists(filename)
    if exist:
        csv_file = open(filename, "a", newline="")
        csv_writer = csv.writer(csv_file)
        for trade in trades:
            row = []
            for element in trades[trade]:
                row.append(trades[trade][element])
            csv_writer.writerow(row)
    else:
        titles = ["ID", "Asset", "Position", "Quantity", "Stop Loss", "Take Profit" ,"Entry Price", "Exit Price", "Entry date", "Exit date", "Entry Time", "Exit Time" ,"Profit","Balance"]
        csv_file = open(filename, "w", newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(titles)
        for trade in trades:
            row = []
            for element in trades[trade]:
                row.append(trades[trade][element])
            csv_writer.writerow(row)
    csv_file.close()
    tradingview.quit()
