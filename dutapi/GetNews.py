
from bs4 import BeautifulSoup, ResultSet
from datetime import datetime
import requests

# Import configured variables
from dutapi.__Variables__ import *
from dutapi.Enums import *
from dutapi.Utils import *

def findList(txt: str, lst: ResultSet):
    index: int = 0
    try:
        for item in lst:
            if txt.text == item.text:
                break
            else:
                index += 1
        if index >= len(lst):
            raise Exception()
    except Exception as ex:
        index = -1
    return index

def GetLinks(src: ResultSet):
    result = []

    # Temporary variables here
    linkResultSet = src.find_all(name='a')
    textLength = 0
    navStringResultSet = src.find_all(text=True)

    for node in navStringResultSet:
        index = findList(node, linkResultSet)
        if (index > -1):
            item = {}
            item['text'] = linkResultSet[index].text
            item['url'] = linkResultSet[index].attrs['href'] if 'href' in linkResultSet[index].attrs.keys() else None
            item['position'] = textLength
            result.append(item)
            linkResultSet.pop(index)
        d1 = len(node.text)
        textLength += d1
    return result


# Get news from sv.dut.udn.vn with page you selected.
def GetNews(type: NewsType = NewsType.Global, page: int = 1):
    """
    Get news from sv.dut.udn.vn.
    For latest news, leave 'page' to default.
    type (NewsType): Type of news want to load.
    page (int): News page. If less than 1, will be reset to 1.
    """
    # Prepare a result data    
    jsonReturn = {}
    jsonReturn['date'] = round(datetime.timestamp(datetime.now()) * 1000, 0)
    jsonReturn['news_type'] = type.value
    jsonReturn['news_list'] = []
    if (page < 1):
        page = 1
    try:
        # Get elements from sv.dut.dut.vn
        if (type == NewsType.Global):
            webHTML = requests.get(URL_NEWSGENERAL.format(page = page))
        else:
            webHTML = requests.get(URL_NEWSSUBJECTS.format(page = page))
        # Convert to BeautifulSoup
        soup = BeautifulSoup(webHTML.content, 'lxml')
        # Find all element groups in html.
        news = soup.findAll('div', {'class': 'tbBox'})
        for i in range(0, len(news), 1):
            # Get news date and title
            webElement = news[i].find('div', class_='tbBoxCaption')
            dateText = webElement.find_all('span')[0].text.replace(':', '')
            dateTextSplit = dateText.split('/')
            date = round(datetime.timestamp(datetime(int(dateTextSplit[2]), int(dateTextSplit[1]), int(dateTextSplit[0]))) * 1000, 0)
            title = webElement.find_all('span')[1].text
            # Get news content
            content = news[i].find('div', class_='tbBoxContent')
            # Add to jsonReturn
            jsonReturn['news_list'].append({
                'date': date,
                'title': title,
                'content': content.text,
                'links': GetLinks(content)
            })
    except:
        # If something went wrong, delete all items in news list.
        jsonReturn['news_list'].clear()
    finally:
        # Return result
        return jsonReturn
