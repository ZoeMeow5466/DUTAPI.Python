
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

# Get current GMT
def GetRegionGMT():
    return round((-time.timezone) / 3600, 1)
