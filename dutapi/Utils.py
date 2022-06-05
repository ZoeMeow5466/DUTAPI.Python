
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import json
import math

# Import configured variables
from dutapi.__Variables__ import *
from dutapi.Enums import *

def GetRegionGMT():
    return round((-time.timezone) / 3600, 1)

# Data from dut.udn.vn.
def GetCurrentWeek(year: int = 21):
    schoolyear_start_json: dict = json.loads(SCHOOLYEAR_START)
    result = None
    try:
        for item in schoolyear_start_json['list']:
            if item['year_id'] == year:
                dt = datetime(item['year'], item['month'], item['day'])
                result = round((datetime.now() - timedelta(hours=GetRegionGMT()) + timedelta(hours=7) - dt).days / 7 + 2, 3)
        if result == None:
            raise Exception("""Invalid 'year' parameters (must be in range (16, 21)).""")
    except Exception as ex:
        result = -1
        print(ex)
    return result

def GetValueFromAccountInformation(soup: BeautifulSoup, id: dict):
    tempHtml = soup.find(id['tag'], {'id': id['id']})
    try:
        if (id['tag'] == 'input'):
            return tempHtml['value']
        elif (id['tag'] == 'select'):
            for tempOption in tempHtml.find_all('option', {'selected': 'selected'}):
                return tempOption.text
        else:
            raise Exception('Undefined')
    except Exception as ex:
        print('Can\'t get {id}: {err}'.format(id=id['id'], err=ex))
        return None
