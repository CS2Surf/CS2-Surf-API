import mysql.connector
import simplejson as json


with open("config.json", "r") as f:
    config = json.load(f)


def selectQuery(query):
    """Executes `SELECT` query provided and returns the output in JSON\n
    Connects to a predefined `Database` from `config.json`"""
    json_data = []
    db = config["DATABASE"]
    mydb = mysql.connector.connect(
        host=db["HOST"],
        user=db["USERNAME"],
        password=db["PASSWORD"],
        database=db["DB"],
    )
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(query)
    res = mycursor.fetchall()
    for result in res:
        json_data.append(dict(result))

    mydb.close()
    return json_data


def insertQuery(query):
    """Executes `INSERT` query provided and returns `mycursor.rowcount`\n
    Connects to a predefined `Database` from `config.json`"""
    db = config["DATABASE"]
    mydb = mysql.connector.connect(
        host=db["HOST"],
        user=db["USERNAME"],
        password=db["PASSWORD"],
        database=db["DB"],
    )

    mycursor = mydb.cursor()
    mycursor.execute(query)

    mydb.commit()

    return mycursor.rowcount


def insert_escaped_query(query):
    """Executes `INSERT` query `mycursor.execute("", (query))` provided and returns `mycursor.rowcount`\n
    Connects to a predefined `Database` from `config.json`"""
    db = config["DATABASE"]
    mydb = mysql.connector.connect(
        host=db["HOST"],
        user=db["USERNAME"],
        password=db["PASSWORD"],
        database=db["DB"],
    )

    mycursor = mydb.cursor()
    mycursor.execute("", (query))

    mydb.commit()

    return mycursor.rowcount


def syncQuery(query):
    db = config["DATABASE"]
    mydb = mysql.connector.connect(
        host=db["HOST"],
        user=db["USERNAME"],
        password=db["PASSWORD"],
    )

    mycursor = mydb.cursor()
    mycursor.execute(query)

    mydb.commit()

    return mycursor.rowcount
