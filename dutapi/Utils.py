
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json

# Import configured variables
from dutapi.__Variables__ import *
from dutapi.Enums import *

# Data from dut.udn.vn.
def GetCurrentWeek(year: int = 21):
    schoolyear_start_json: dict = json.loads(SCHOOLYEAR_START)
    if str(year) in schoolyear_start_json.keys():
        dt = datetime(schoolyear_start_json[str(year)]['year'], schoolyear_start_json[str(year)]['month'], schoolyear_start_json[str(year)]['day'])
    else:
        raise Exception("""Invalid 'year' parameters (must be in range (16, 21)).""")
    return round((datetime.now() - dt).days / 7 + 1)

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
