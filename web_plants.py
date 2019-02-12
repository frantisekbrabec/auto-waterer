from flask import Flask, render_template
import json
import sqlite3
from collections import defaultdict
import random
import os

with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
    SETTINGS = json.load(f)

app = Flask(__name__)

def constant_factory():
    return lambda: {"plantid": 0, "data": []}

def getDistinctColor(index, offset):
    # use 0/1 offset to draw one of four sets of options
    distinct_colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6']
    return distinct_colors[(4 * offset) + (index % 4)];


@app.route("/")
def chart():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'water_stats.db'))
    c = conn.cursor()

    randomcolorseed = 0;

    plantnames = defaultdict(dict)
    for p in SETTINGS["PLANTS"]:
        plantnames[p['PLANT_ID']] = p['PLANT_NAME']        

    moisturedata = defaultdict(constant_factory())
    for row in c.execute('select id, plantid, datetime(datetime, \'localtime\'), measurement from moisture where datetime > datetime(\'now\',\'-10 days\')'):
        item = {"x": row[2], "y": row[3]} 
        moisturedata[row[1]]["data"].append(item)
        moisturedata[row[1]]["plantid"] = plantnames[row[1]] if plantnames[row[1]] else "Unknown sensor"
        moisturedata[row[1]]["color"] = getDistinctColor(row[1], 0)

    pumpdata = defaultdict(constant_factory())
    # only fetch pump on events
    for row in c.execute('select id, plantid, datetime(datetime, \'localtime\'),status from waterings where datetime > datetime(\'now\',\'-10 days\')'):
        item = {"x": row[2], "y": row[3]}
        pumpdata[row[1]]["data"].append(item)
        pumpdata[row[1]]["plantid"] = plantnames[row[1]] if plantnames[row[1]] else "Unknown pump"
        pumpdata[row[1]]["color"] = getDistinctColor(row[1], 1)

    return render_template('moisture.html', pumpdata = pumpdata, moisturedata = moisturedata)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
