def createDB(dbcursor):
    """
    创建项目数据库
    """
    dbcursor.execute("CREATE DATABASE if not exists `projectdatabase`")



def createTB(dbcursor):

    """
    逐个建表
    如果要修改表结构
    建议大家把不是自己负责的表注释掉
    在自己的分支里修改表的基本信息
    """

    dbcursor.execute(  # 构建用户数据表
        "CREATE TABLE if not exists ProjectDataBase.UserData(\
            UserID varchar(32) unique,\
            account varchar(32) unique,\
            Password varchar(128),\
            primary key(UserID)\
        )\
        ENGINE = InnoDB\
        DEFAULT CHARSET = utf8\
        COLLATE = utf8_general_ci;\
        "

    )

    dbcursor.execute(  # 构建渔民数据表
        "CREATE TABLE if not exists ProjectDataBase.FisherData(\
            FisherID smallint unique,\
            UserID varchar(32),\
            primary key(FisherID)\
        )\
        ENGINE = InnoDB\
        DEFAULT CHARSET = utf8\
        COLLATE = utf8_general_ci;\
        "
    )

    dbcursor.execute(  # 构建鱼类数据表
        "CREATE TABLE if not exists ProjectDataBase.AllFishData(\
            FishID smallint unique,\
            Species varchar(32),\
            Weight float,\
            Length1 float,\
            Length2 float,\
            Length3 float,\
            Height float,\
            Width float,\
            FisherID smallint DEFAULT -1,\
            primary key(FishID)\
        )\
        ENGINE = InnoDB\
        DEFAULT CHARSET = utf8\
        COLLATE = utf8_general_ci;\
        "
    )

    dbcursor.execute(   # 构建水质数据表
        "CREATE TABLE if not exists ProjectDataBase.WaterData(\
            Province varchar(256),\
            Location varchar(256),\
            Domain varchar(256),\
            Time varchar(256),\
            WaterType smallint,\
            Temperature float,\
            PH float,\
            Oxygen float,\
            Conductivity float,\
            Turbidity float,\
            KMnO4 float,\
            NH4 float,\
            All_P float,\
            All_N float,\
            IAA float,\
            Cells float,\
            Status float,\
            UNIQUE (Province, Location, Domain, Time)\
        )\
        ENGINE = InnoDB\
        DEFAULT CHARSET = utf8\
        COLLATE = utf8_general_ci;\
        "
    )

    dbcursor.execute(   # 构建天气数据表
        "CREATE TABLE if not exists ProjectDataBase.WeatherData(\
            Province varchar(256),\
            Location varchar(256),\
            Domain varchar(256),\
            Time varchar(256),\
            TemperatureHigh float,\
            TemperatureLow float,\
            WindLevel float,\
            AQI varchar(32),\
            Light smallint,\
            Humidity smallint,\
            UNIQUE (Province, Location, Domain, Time)\
        )\
        ENGINE = InnoDB\
        DEFAULT CHARSET = utf8\
        COLLATE = utf8_general_ci;\
        "
    )

    dbcursor.execute(   # 构建设备数据表
        "CREATE TABLE if not exists ProjectDataBase.DeviceData(\
            DeviceID smallint unique,\
            DeviceNumber smallint,\
            DeviceData varchar(256),\
            DeviceStatus varchar(256),\
            primary key(DeviceID)\
        )\
        ENGINE = InnoDB\
        DEFAULT CHARSET = utf8\
        COLLATE = utf8_general_ci;\
        "
    )

    dbcursor.execute(   # 构建系统信息数据表
        "CREATE TABLE if not exists ProjectDataBase.SystemData(\
            DataID smallint unique,\
            MemoryUsed bigint,\
            MemoryAll bigint,\
            SystemStatus varchar(32),\
            Time varchar(256),\
            primary key(DataID)\
        )\
        ENGINE = InnoDB\
        DEFAULT CHARSET = utf8\
        COLLATE = utf8_general_ci;\
        "
    )