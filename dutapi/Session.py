
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
from requests.structures import CaseInsensitiveDict
	
# Import configured variables
from dutapi.__Variables__ import *
from dutapi.Enums import *
from dutapi.Utils import *
from dutapi.AccountColumnInfo import *

def GenerateSessionID():
    WEB_SESSION = requests.Session()
    response = WEB_SESSION.get('http://sv.dut.udn.vn')
    if (response.status_code in [200, 204]):
        temp = WEB_SESSION.cookies.get_dict()
        if ('ASP.NET_SessionId' in temp.keys()):
            return temp['ASP.NET_SessionId']

def IsLoggedIn(sessionID: str):
    """
    Check if your account is logged in from sv.dut.udn.vn.
    """
    # Prepare a result data.
    result = {}
    result['date'] = round(datetime.timestamp(datetime.now()) * 1000, 0)
    result['session_id'] = sessionID
    result['logged_in'] = False
    try:
        # If session id is not exist, create one
        headers = CaseInsensitiveDict()
        headers["Cookie"] = "ASP.NET_SessionId={id};".format(id=sessionID)
        response = requests.get(URL_ACCOUNTCHECKLOGIN, headers=headers) 
        if (response.status_code in [200, 204]):
            result['logged_in'] = True
    except:
        # If something went wrong, 'loggedin' will False.
        result['logged_in'] = False
    finally:
        # Return result
        return result

def Login(sessionID: str, username: str, password: str):
    """
    Login to sv.dut.udn.vn using your account provided by DUT school.
    username (string): Username (i.e. Student ID).
    password (string): Password
    """
    # 
    dataRequest = {}
    dataRequest['__VIEWSTATE'] = VIEWSTATE
    dataRequest['__VIEWSTATEGENERATOR'] = '20CC0D2F'
    dataRequest['_ctl0:MainContent:DN_txtAcc'] = username
    dataRequest['_ctl0:MainContent:DN_txtPass'] = password
    dataRequest['_ctl0:MainContent:QLTH_btnLogin'] = 'Đăng+nhập'
    # print(self.SessionID)
    headers = CaseInsensitiveDict()
    headers["Cookie"] = "ASP.NET_SessionId={id};".format(id=sessionID)
    requests.post(URL_ACCOUNTLOGIN, data=dataRequest, headers=headers)
    #
    return IsLoggedIn(sessionID)

def Logout(sessionID: str):
    """
    Logout your account from sv.dut.udn.vn.
    """
    headers = CaseInsensitiveDict()
    headers['Cookie'] = "ASP.NET_SessionId={id}".format(id=sessionID)
    requests.get(URL_ACCOUNTLOGOUT, headers=headers)
    #
    return IsLoggedIn(sessionID)

def __string2ExamSchedule__(src: str):
    # If string is empty, return {}
    if (len(src.replace(' ', '')) == 0):
        return {
            'examDate': None,
            'examRoom': None
        }
    # Split string.
    dateSplitted = src.split(', ')
    dataList = []
    for item in dateSplitted:
        dataList.append({
            'type': item.split(': ')[0],
            'value': item.split(': ')[1]
        })
    # Preprocessing
    date = datetime(2000, 1, 1)
    room = None
    for item in dataList:
        if item['type'] == 'Ngày':
            splitted = item['value'].split('/')
            if len(splitted) == 3:
                date = date.replace(year=int(splitted[2]), month=int(splitted[1]), day=int(splitted[0]))
        elif item['type'] == 'Phòng':
            room = item['value']
        elif item['type'] == 'Giờ':
            splitted = item['value'].split('h')
            if len(splitted) > 0:
                date = date.replace(hour=int(splitted[0]))
            if len(splitted) > 1:
                date = date.replace(minute=int(splitted[1]))
    date = date - timedelta(hours=7) + timedelta(hours=GetRegionGMT())
    # Return
    result = {}
    result['examDate'] = round(datetime.timestamp(date) * 1000, 0)
    result['examRoom'] = room
    return result

def GetSubjectSchedule(sessionID: str, year: int = 20, semester: int = 1, studyAtSummer: bool = False):
    """
    Get all subject schedule (study and examination) from a year you choosed.
    year (int): 2-digit year.
    semester (int): 1 or 2
    studyAtSummer (bool): Show schedule if you has studied in summer. 'semester' must be 2, otherwise will getting exception.
    """
    result = {}
    result['date'] = round(datetime.timestamp(datetime.now()) * 1000, 0)
    result['total_credit'] = 0.0
    result['schedule_list'] = []
    try:
        if (IsLoggedIn(sessionID) == False):
            raise Exception('Page isn\'t load successfully.')
        if studyAtSummer:
            satS = 1
        else:
            satS = 0
        url = URL_ACCOUNTSCHEDULE.format(nam = year, hocky = semester, hoche = satS)
        headers = CaseInsensitiveDict()
        headers['Cookie'] = "ASP.NET_SessionId={id}".format(id=sessionID)
        webHTML = requests.get(url, headers=headers)
        soup = BeautifulSoup(webHTML.content, 'lxml')
        # Find all subjects schedule
        schStudyTable = soup.find('table', {'id': 'TTKB_GridInfo'})
        schStudyRow = schStudyTable.find_all('tr', {'class': 'GridRow'})
    
        for i in range(0, len(schStudyRow) - 1, 1):
            cell = schStudyRow[i].find_all('td', {'class':'GridCell'})
            resultRow = {}
            # ID
            resultRow['id'] = cell[1].text
            # Name
            resultRow['name'] = cell[2].text
            # Credit
            resultRow['credit'] = float(cell[3].text)
            # Is High Quality
            resultRow['is_high_quality'] = True if ('GridCheck' in cell[5].attrs.get('class')) else False
            # Lecturer name
            resultRow['lecturer'] = cell[6].text
            # Schedule study area
            resultRow['schedule_study'] = {}
            # Schedule study
            if (cell[7].text != None and len(cell[7].text) > 0):
                resultRow['schedule_study']['schedule'] = []
                cellSplit = cell[7].text.split('; ') if ('; ' in cell[7].text) else [cell[7].text]
                for cellSplitItem in cellSplit:
                    item = {}
                    item['day_of_week'] = 0 if ('CN' in cellSplitItem.upper()) else (int(cellSplitItem.split(',')[0].split(' ')[1]) - 1)
                    item['lesson'] = {}
                    item['lesson']['start'] = cellSplitItem.split(',')[1].split('-')[0]
                    item['lesson']['end'] = cellSplitItem.split(',')[1].split('-')[1]
                    item['room'] = cellSplitItem.split(',')[2]
                    resultRow['schedule_study']['schedule'].append(item)
            else:
                resultRow['schedule_study']['schedule'] = None
            # Weeks
            if (cell[8].text != None and len(cell[8].text) > 0):
                resultRow['schedule_study']['weeks'] = []
                cellSplit = cell[8].text.split(';') if (';' in cell[8].text) else [cell[8].text]
                for cellSplitItem in cellSplit:
                    item = {}
                    item['start'] = cellSplitItem.split('-')[0]
                    item['end'] = cellSplitItem.split('-')[1]
                    resultRow['schedule_study']['weeks'].append(item)
            else:
                resultRow['schedule_study']['weeks'] = None
            # Point formula
            resultRow['point_formula'] = cell[10].text
            # Plus credit to total
            result['total_credit'] += resultRow['credit']
            # Append to schedule list
            result['schedule_list'].append(resultRow)
        
        # Find all subjects schedule examination
        schExamTable = soup.find('table', {'id': 'TTKB_GridLT'})
        schExamRow = schExamTable.find_all('tr', {'class': 'GridRow'})

        for i in range(0, len(schExamRow), 1):
            cell = schExamRow[i].find_all('td', {'class':'GridCell'})
            for j in range(0, len(result['schedule_list']), 1):
                if (result['schedule_list'][j]['id'] == cell[1].text):
                    result['schedule_list'][j]['schedule_exam'] = {}
                    result['schedule_list'][j]['schedule_exam']['group'] = cell[3].text
                    result['schedule_list'][j]['schedule_exam']['is_global'] = True if ('GridCheck' in cell[4].attrs.get('class')) else False
                    result['schedule_list'][j]['schedule_exam']['date'] = __string2ExamSchedule__(cell[5].text)['examDate']
                    result['schedule_list'][j]['schedule_exam']['room'] = __string2ExamSchedule__(cell[5].text)['examRoom']
    except Exception as ex:
        result['total_credit'] = 0.0
        result['schedule_list'].clear()
        print(ex)
    finally:
        return result

def GetSubjectFee(sessionID: str, year: int = 20, semester: int = 1, studyAtSummer: bool = False):
    """
    Get all subject fee from a year you choosed.
    year (int): 2-digit year.
    semester (int): 1 or 2
    studyAtSummer (bool): Show schedule if you has studied in summer. 'semester' must be 2, otherwise will getting exception.
    """
    result = {}
    result['date'] = round(datetime.timestamp(datetime.now()) * 1000, 0)
    result['total_credit'] = 0
    result['total_money'] = 0
    result['fee_list'] = []
    try:
        if (IsLoggedIn(sessionID) == False):
            raise Exception('You are not logged in.')
        headers = CaseInsensitiveDict()
        headers['Cookie'] = "ASP.NET_SessionId={id}".format(id=sessionID)
        webHTML = requests.get(URL_ACCOUNTFEE.format(nam = year, hocky = semester, hoche = 1 if (studyAtSummer) else 0), headers=headers)
        soup = BeautifulSoup(webHTML.content, 'lxml')
        # Find all subjects fees
        feeTable = soup.find('table', {'id': 'THocPhi_GridInfo'})
        feeRow = feeTable.find_all('tr', {'class': 'GridRow'})
        for i in range (0, len(feeRow) - 1, 1):
            cell = feeRow[i].find_all('td', {'class':'GridCell'})
            item = {}
            item['id'] = cell[1].text
            item['name'] = cell[2].text
            item['credit'] = float(cell[3].text)
            item['is_high_quality'] = True if ('GridCheck' in cell[4].attrs.get('class')) else False
            item['price'] = 0 if (cell[5].text == None or len(cell[5].text) == 0) else float(cell[5].text.replace(',', ''))
            item['debt'] = True if ('GridCheck' in cell[6].attrs.get('class')) else False
            item['is_restudy'] = True if ('GridCheck' in cell[7].attrs.get('class')) else False
            item['verified_payment_at'] = cell[8].text
            result['total_credit'] += item['credit']
            result['total_money'] += item['price']
            result['fee_list'].append(item)
    except Exception as ex:
        result['total_credit'] = 0
        result['total_money'] = 0
        result['fee_list'] = []
        print(ex)
    finally:
        return result

def __getStudentID__(soup: BeautifulSoup):
    baseTxt = soup.find('span', {'id': 'Main_lblHoTen'}).text
    return baseTxt[baseTxt.index('(') + 1:baseTxt.index(')')]

def GetAccountInformation(sessionID: str):
    result = {}
    result['date'] = round(datetime.timestamp(datetime.now()) * 1000, 0)
    result['account_info'] = {}
    try:
        if (IsLoggedIn(sessionID) == False):
            raise Exception('You are not logged in.')
        headers = CaseInsensitiveDict()
        headers['Cookie'] = "ASP.NET_SessionId={id}".format(id=sessionID)
        webHTML = requests.get(URL_ACCOUNTINFORMATION, headers=headers)
        soup = BeautifulSoup(webHTML.content, 'lxml')
        for col in accInfoCol:
            result['account_info'][col['jsname']] = GetValueFromAccountInformation(soup, col)
        result['account_info']['studentId'] = __getStudentID__(soup)
    except Exception as ex:
        print(ex)
    finally:
        return result
        