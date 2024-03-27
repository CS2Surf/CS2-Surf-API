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

    # Get the last auto-incremented value
    last_inserted_id = mycursor.lastrowid

    return mycursor.rowcount, last_inserted_id


def insertEscapedQuery(query):
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

    # Get the last auto-incremented value
    last_inserted_id = mycursor.lastrowid

    return mycursor.rowcount, last_inserted_id


def executeTransaction(queries):
    """Executes multiple queries within a single transaction and returns the row counts"""
    db_config = config["DATABASE"]
    mydb = mysql.connector.connect(
        host=db_config["HOST"],
        user=db_config["USERNAME"],
        password=db_config["PASSWORD"],
        database=db_config["DB"],
    )

    try:
        mycursor = mydb.cursor()

        # Start a transaction
        mydb.start_transaction()

        row_counts = []

        for query in queries:
            mycursor.execute(query)
            row_counts.append(mycursor.rowcount)

        # Commit the transaction
        mydb.commit()

        return row_counts

    except Exception as e:
        # Rollback the transaction if an error occurs
        mydb.rollback()
        raise e

    finally:
        mydb.close()
