import pymongo
import json
import pandas as pd
import numpy as np
from pymongo import MongoClient
from flask import Flask, request

from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
import requests
application = Flask(__name__)


@application.route("/get")
def get_value():
    dist = request.args.get('dist')
    state = request.args.get('state')
    day = request.args.get('day')
    time = request.args.get('time')
    client = MongoClient(
        'mongodb+srv://chirag:6398356528@cluster0.gha33.mongodb.net/CRM?retryWrites=true&w=majority')
    db = client["CRM"]
    mycollection = db["firs"]
    df = pd.DataFrame(list(mycollection.find()))
    # print(df)
    dd = df['crimeDetails']
    final_df = pd.DataFrame()

    for i in range(0, df.shape[0]):
        new = pd.DataFrame.from_dict([dd[i]])
        if final_df.empty:
            final_df = new
            # print(final_df)
        else:
            final_df = pd.concat([final_df, new])
            #final_df = final_df.append(new, ignore_index=True)

    final_df['time'] = final_df['time'].str.split(
        ":").apply(lambda x: int(x[0]) * 60 + int(x[1]))
    dfrun = final_df[final_df.district == dist]
    print(final_df)
    dfrun = dfrun.drop(
        ['suspected', 'crime', 'district', 'date', 'state', 'pinCode', 'address'], axis=1)
    dfrun['day'].replace({"Monday": 1, "Tuesday": 2, "Wednesday": 3,
                          "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}, inplace=True)
    X_train = dfrun.drop(columns='colony')
    Y_train = dfrun['colony']
    dt = DecisionTreeClassifier()
    model = dt.fit(X_train, Y_train)
    data = [[time, day]]
    X_test = pd.DataFrame(data, columns=['time', 'day', ])
    X_test['day'].replace({"Monday": 1, "Tuesday": 2, "Wednesday": 3,
                          "Thursday": 4, "Friday": 5, "Saturday": 6, "Sunday": 7}, inplace=True)
    X_test['time'] = X_test['time'].str.split(
        ":").apply(lambda x: int(x[0]) * 60 + int(x[1]))
    area = model.predict(X_test)
    str1 = ""
    for ele in area:
        str1 += ele
    url = 'https://api.radar.io/v1/geocode/forward?query=' + \
        '+'+str1+'+'+dist+'+'+state+'+'+'India'
    str1 = str1+","+dist+","+state
    headers = {
        'Authorization': 'prj_live_pk_2524016d5c714b2ae4c77164cab1a55ca8c8ec16'}
    response = requests.get(url, headers=headers)
    meta = json.loads(response.content)
    return {'Address': str1,
            'Location': meta}


verhoeff_table_d = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0))
verhoeff_table_p = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8))
verhoeff_table_inv = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def calcsum(number):
    c = 0
    for i, item in enumerate(reversed(str(number))):
        c = verhoeff_table_d[c][verhoeff_table_p[(i+1) % 8][int(item)]]
    return verhoeff_table_inv[c]


def checksum(number):
    c = 0
    for i, item in enumerate(reversed(str(number))):
        c = verhoeff_table_d[c][verhoeff_table_p[i % 8][int(item)]]
    return c


def generateVerhoeff(number):
    return "%s%s" % (number, calcsum(number))


def validateVerhoeff(number):
    return checksum(number) == 0


@application.route("/aadhaar")
def aadhaar():
    num = request.args.get('number')
    if (validateVerhoeff(num)):
        return "Valid"
    else:
        return "Invalid"


if __name__ == "__main__":
    application.run(debug=True)
