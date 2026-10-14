import sqlite3
import hashlib
import datetime

def check_for_db():
    account = sqlite3.connect("accounts.db")
    cursor = account.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS accounts (
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                tutorial INTEGER,
                date_created DATETIME,
                wins INTEGER,
                losses INTEGER,
                winloss REAL,
                PRIMARY KEY(username)
                )""")
    cursor.execute(""" CREATE TABLE IF NOT EXISTS times (
                time REAL,
                timeID INTEGER UNIQUE,
                difficulty TEXT,
                obtain_date DATETIME,
                username TEXT,
                PRIMARY KEY(timeID AUTOINCREMENT),
                FOREIGN KEY(username) REFERENCES accounts(username)
                )""")
    account.commit()

def check_for_username(user):
    account = sqlite3.connect("accounts.db")
    cursor = account.cursor()
    data = {"user":user}
    cursor.execute("SELECT * FROM accounts WHERE username=:user", data)
    taken  = cursor.fetchall()
    return taken

def insert_account(user, password, tutorial_completion):
    account = sqlite3.connect("accounts.db")
    cursor = account.cursor()
    hashed_password = hashlib.sha224(password.encode("utf-8")).hexdigest()
    current_date = datetime.datetime.today().strftime('%d-%m-%Y')
    data = {"user":user,"password":hashed_password,"tutorial_completion":tutorial_completion, "creation_date":current_date}
    cursor.execute("INSERT INTO accounts VALUES (:user, :password, :tutorial_completion, :creation_date, 0, 0, 0)", data)
    account.commit()

def insert_time(user, time, difficulty):
    times = sqlite3.connect("accounts.db")
    cursor = times.cursor()
    current_date = datetime.datetime.today().strftime('%d-%m-%Y')
    x = datetime.datetime.strptime(current_date, "%d-%m-%Y").date()
    data = {"time":time,"difficulty":difficulty,"obtain_date":x,"user":user}
    cursor.execute("INSERT INTO times VALUES (:time, NULL, :difficulty, :obtain_date, :user)", data)
    times.commit()

def check_password(user, password):
    account = sqlite3.connect("accounts.db")
    cursor = account.cursor()
    try:
        hashed_password =  hashlib.sha224(password.encode("utf-8")).hexdigest()
        data = {"user":user}
        cursor.execute("SELECT password FROM accounts WHERE username=:user", data)
        saved_password = cursor.fetchone()
        if hashed_password == saved_password[0]:
            return True
        else:
            return False
    except:
        return "error"

def get_average(user):
    account = sqlite3.connect("accounts.db")
    cursor = account.cursor()
    data = {"user":user}
    cursor.execute("SELECT AVG(time) FROM times JOIN accounts ON times.username = accounts.username WHERE accounts.username=:user", data)
    average = cursor.fetchone()
    return average

def get_user(user):
    account = sqlite3.connect("accounts.db")
    cursor = account.cursor()
    data = {"user":user}
    cursor.execute("SELECT * FROM accounts WHERE username=:user", data)
    username = cursor.fetchone()
    return username

def increment(user, WorL):
    account = sqlite3.connect("accounts.db")
    cursor = account.cursor()
    data = {"user":user}
    cursor.execute("SELECT wins FROM accounts WHERE username=:user", data)
    wins = cursor.fetchone()
    cursor.execute("SELECT losses FROM accounts WHERE username=:user", data)
    losses = cursor.fetchone()
    if WorL == "w":      
        winsadd = wins[0] + 1
        data = {"user":user,"wins":winsadd}
        cursor.execute("UPDATE accounts SET wins=:wins WHERE username=:user", data)
        account.commit()
    elif WorL == "l":
        lossesadd = losses[0] + 1
        data = {"user":user,"losses":lossesadd}
        cursor.execute("UPDATE accounts SET losses=:losses WHERE username=:user", data)
        account.commit()
    if losses[0] == 0 and WorL == "w":
        winloss = winsadd
        data = {"user":user,"winloss":winloss}
    elif losses[0] != 0 and WorL == "w":
        winloss = winsadd / losses[0]
        data = {"user":user,"winloss":winloss}
    elif WorL == "l":
        winloss = wins[0] / lossesadd
        data = {"user":user,"winloss":winloss}
    cursor.execute("UPDATE accounts SET winloss=:winloss WHERE username=:user", data)
    account.commit()

def update_tutorial(user):
    account = sqlite3.connect("accounts.db")
    cursor = account.cursor()
    data = {"user":user,"tutorial":1}
    cursor.execute("UPDATE accounts SET tutorial=:tutorial WHERE username=:user", data)
    account.commit()

def get_leaderboard(difficulty, time):
    account = sqlite3.connect("accounts.db")
    cursor = account.cursor()
    if time == "All-time":
        data = {"difficulty":difficulty}
        cursor.execute("SELECT time,timeID,username FROM times WHERE difficulty=:difficulty",data)
        times = cursor.fetchall()
        return times
    if time == "Monthly":
        current_date = datetime.datetime.today().strftime("%d-%m-%Y")
        x = datetime.datetime.strptime(current_date, "%d-%m-%Y").date()
        month_date = x - datetime.timedelta(days=30)
        data = {"difficulty":difficulty,"last_date":month_date}
    if time == "Weekly":
        current_date = datetime.datetime.today().strftime("%d-%m-%Y")
        x = datetime.datetime.strptime(current_date, "%d-%m-%Y").date()
        week_date = x - datetime.timedelta(weeks=1)
        data = {"difficulty":difficulty,"last_date":week_date}
    cursor.execute("SELECT time,timeID,username FROM times WHERE obtain_date>=:last_date AND difficulty=:difficulty", data)
    times = cursor.fetchall()
    return times

def sort_leaderboard(times):
    if len(times) > 1:
        left_times = times[:len(times)//2]
        right_times = times[len(times)//2:]
        sort_leaderboard(left_times)
        sort_leaderboard(right_times)
        i = 0
        j = 0
        k = 0
        while i < len(left_times) and j < len(right_times):
            if left_times[i][0] < right_times[j][0]:
                times[k] = left_times[i]
                i += 1
            else:
                times[k] = right_times[j]
                j += 1
            k += 1
        while i < len(left_times):
            times[k] = left_times[i]
            i += 1
            k += 1
        while j < len(right_times):
            times[k] = right_times[j]
            j += 1
            k += 1