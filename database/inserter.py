def insertfishdata(dbcursor, values):
    sql = "INSERT INTO ProjectDataBase.AllFishData (" \
          "Species," \
          "Weight," \
          "Length1," \
          "Length2," \
          "Length3," \
          "Height," \
          "Width," \
          "FishID) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    dbcursor.execute(sql, values)