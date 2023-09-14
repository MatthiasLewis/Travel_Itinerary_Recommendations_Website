from sqlalchemy import create_engine
from datetime import timedelta
import pandas as pd 


engine = create_engine("sqlite:///travel.db?charset=utf8")

def get_table(args):
    """
    依需求連結指定table取值，並放入pandas。 
    """
    df = pd.read_sql(args,engine)
    engine.dispose()
    return df

def get_traveldates(date):
    """
    依照天數安排每天應有行程數及行程格式，並統計各type的數量。
    """
    days = []
    for i in range(date):
        if date<=1 and i+1 >= date:
            oneday = {f"day{i+1}":[None,
                        {"morning_time":None,
                        "lunch":None,
                        "afternoon_time1":None,
                        "afternoon_time2":None,
                        "dinner":None}]}
        elif i+1 == date:
            oneday = {f"day{i+1}":[None,
                        {"morning_time":None,
                        "lunch":None,
                        "afternoon_time1":None,
                        "afternoon_time2":None}]}
        else:
            oneday = {f"day{i+1}":[None,
                        {"morning_time":None,
                        "lunch":None,
                        "afternoon_time1":None,
                        "afternoon_time2":None,
                        "dinner":None,
                        "hotel":None}]}
        days.append(oneday)

    if len(days)==1:
        times = {"food":2,"hotel":0,"view":3}  
    else:    
        times = {"food":(len(days)-1)*2+1,"hotel":len(days)-1,"view":len(days)*3}

    return days,times

def getdatetime(dates,input,departure_date,return_date):
    if departure_date == 0 : return input,0
    alldays=[]
    if dates>2:
        startd=departure_date
        while True:
            alldays.append(startd.strftime("%Y-%m-%d"))
            startd=startd+timedelta(days=1)
            if startd > return_date: break
    else:
        alldays=[departure_date.strftime("%Y-%m-%d"),return_date.strftime("%Y-%m-%d")]
    for i,_ in enumerate(input):
        input[i][f"day{i+1}"][0]=alldays[i]
    return input,alldays
