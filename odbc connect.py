def dataPull(queryFile):
    import pypyodbc
    import pandas

    # Using pypyodbc driver creating hive connection
    hiveConnection = pypyodbc.connect(DSN="Hive_DB64", autocommit=True)

    # Opening a cursor
    cur = hiveConnection.cursor()

    # Reading query String from the file
    with open (queryFile, "r") as query:
        query = str(query.read())

    print("Fetching data")

    # Running the Query from Hive
    data = pandas.DataFrame(cur.execute(query).fetchall())
    data.columns  = [hdrs[0] for hdrs in cur.description ]

    return data