
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
from requests.structures import CaseInsensitiveDict
	
# Import configured variables
from dutapi.__Variables__ import *
from dutapi.Enums import *
from dutapi.Utils import *

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
    result['sessionid'] = sessionID
    result['loggedin'] = False
    try:
        # If session id is not exist, create one
        headers = CaseInsensitiveDict()
        headers["Cookie"] = "ASP.NET_SessionId={id};".format(id=sessionID)
        response = requests.get(URL_ACCOUNTCHECKLOGIN, headers=headers) 
        if (response.status_code in [200, 204]):
            result['loggedin'] = True
    except:
        # If something went wrong, 'loggedin' will False.
        result['loggedin'] = False
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

def __TableRowToJson__(row, dataInput):
    result = {}
    try:
        cell = row.find_all('td', {'class':'GridCell'})
        for i in range(0, len(dataInput), 1):
            if (dataInput[i][2].lower() == 'num'):
                try:
                    result[dataInput[i][0]] = float(cell[dataInput[i][1]].text.replace(',',''))
                except:
                    result[dataInput[i][0]] = 0
            elif (dataInput[i][2].lower() == 'bool'):
                if 'GridCheck' in cell[dataInput[i][1]].attrs.get('class'):
                    result[dataInput[i][0]] = True
                else:
                    result[dataInput[i][0]] = False
            elif (dataInput[i][2].lower() == 'string'):
                result[dataInput[i][0]] = cell[dataInput[i][1]].text
            else:
                pass
        pass
    except:
        result = {}
    finally:
        return result

def __string2ExamSchedule__(src: str, gmt = 7.0):
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
    date = date - timedelta(seconds=int((GetRegionGMT() * 3600))) + timedelta(seconds=int(gmt * 3600))
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
    result['totalcredit'] = 0.0
    result['schedulelist'] = []
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
        # Find all subjects schedule when study
        schStudyTable = soup.find('table', {'id': 'TTKB_GridInfo'})
        schStudyRow = schStudyTable.find_all('tr', {'class': 'GridRow'})
        dataSchStudy = [
            ['ID', 1, 'string'],
            ['Name', 2, 'string'],
            ['Credit', 3, 'num'],
            ['IsHighQuality', 5, 'bool'],
            ['Lecturer', 6, 'string'],
            ['ScheduleStudy', 7, 'string'],
            ['Weeks', 8, 'string'],
            ['PointFomula', 10, 'string']
        ]
        for i in range(0, len(schStudyRow) - 1, 1):
            resultRow = __TableRowToJson__(schStudyRow[i], dataSchStudy)
            result['totalcredit'] += resultRow['Credit']
            result['schedulelist'].append(resultRow)
        # Find all subjects schedule examination
        schExamTable = soup.find('table', {'id': 'TTKB_GridLT'})
        schExamRow = schExamTable.find_all('tr', {'class': 'GridRow'})
        dataSchExam = [
            ['ID', 1, 'string'],
            ['Name', 2, 'string'],
            ['GroupExam', 3, 'string'],
            ['IsGlobalExam', 4, 'bool'],
            ['DateExamInString', 5, 'string']
        ]
        for i in range(0, len(schExamRow), 1):
            resultRow = __TableRowToJson__(schExamRow[i], dataSchExam)
            for j in range (0, len(result['schedulelist']), 1):
                if result['schedulelist'][i]['Name'] == resultRow['Name']:
                    result['schedulelist'][i]['GroupExam'] = resultRow['GroupExam']
                    result['schedulelist'][i]['IsGlobalExam'] = resultRow['IsGlobalExam']
                    result['schedulelist'][i]['DateExam'] = __string2ExamSchedule__(resultRow['DateExamInString'], GetRegionGMT())['examDate']
                    result['schedulelist'][i]['RoomExam'] = __string2ExamSchedule__(resultRow['DateExamInString'], GetRegionGMT())['examRoom']
    except Exception as ex:
        result['totalcredit'] = 0.0
        result['schedulelist'].clear()
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
    result['totalcredit'] = 0
    result['totalmoney'] = 0
    result['feelist'] = []
    try:
        if (IsLoggedIn(sessionID) == False):
            raise Exception('Page isn\'t load successfully.')
        if studyAtSummer:
            satS = 1
        else:
            satS = 0
        headers = CaseInsensitiveDict()
        headers['Cookie'] = "ASP.NET_SessionId={id}".format(id=sessionID)
        webHTML = requests.get(URL_ACCOUNTFEE.format(nam = year, hocky = semester, hoche = satS), headers=headers)
        soup = BeautifulSoup(webHTML.content, 'lxml')
        # Find all subjects fees
        feeTable = soup.find('table', {'id': 'THocPhi_GridInfo'})
        feeRow = feeTable.find_all('tr', {'class': 'GridRow'})
        dataInput = [
            ['ID', 1, 'string'],
            ['Name', 2, 'string'],
            ['Credit', 3, 'num'],
            ['IsHighQuality', 4, 'bool'],
            ['Price', 5, 'num'],
            ['Debt', 6, 'bool'],
            ['IsReStudy', 7, 'bool'],
            ['VerifiedPaymentAt', 8, 'string']
        ]
        for i in range(0, len(feeRow) - 1, 1):
            resultRow = __TableRowToJson__(feeRow[i], dataInput)
            result['totalcredit'] += resultRow['Credit']
            result['totalmoney'] += resultRow['Price']
            result['feelist'].append(resultRow)
    except:
        result['totalcredit'] = 0
        result['totalmoney'] = 0
        result['feelist'] = []
    finally:
        return result
