import re
import requests
import imgkit
import time
from xml.sax import saxutils as su
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime


headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

titles = ['National_responses_to_the_COVID-19_pandemic',
          'COVID-19_vaccine',
          'Workplace_hazard_controls_for_COVID-19',
          'COVID-19_pandemic_in_the_United_States',
          'COVID-19_pandemic_in_Brazil',
          'COVID-19_pandemic_in_India',
          'COVID-19_pandemic_in_Russia',
          'COVID-19_pandemic_in_South_Africa',
          'COVID-19_pandemic_in_Peru',
          'COVID-19_pandemic_in_Mexico',
          'COVID-19_pandemic_in_Chile',
          'COVID-19_pandemic_in_the_United_Kingdom',
          'COVID-19_pandemic_in_Iran',
          'Severe_acute_respiratory_syndrome_coronavirus_2',
          'Coronavirus',
          'COVID-19_pandemic',
          'Coronavirus_disease_2019',
          'Coronavirus_disease',
          'COVID-19_recession',
          'List_of_unproven_methods_against_COVID-19']

mostRecent = {}


def checkSize(curr):
    diffBytes = curr.find('span', class_='mw-diff-bytes', dir='ltr')

    if diffBytes:
        size = diffBytes.get_text()
        return abs(int(size)) >= 300
    else:
        return


def createTweet(curr):

    if checkSize(curr) == True:
        link = curr.span.find('a', href=True)
        href = 'https://en.wikipedia.org/' + link['href']

        req = requests.get(href, headers)

        soup = BeautifulSoup(req.content, 'lxml')

    # find table
        title = soup.find("h1", id="firstHeading").get_text()
        table = soup.find('table')
        tableRows = table.find_all('tr')

        # loop   through table rows
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y%H:%M:%S")

        for tableRow in tableRows:
            deletedLine = tableRow.find(class_='diff-deletedline')
            addedLine = tableRow.find(class_='diff-addedline')
            if deletedLine != None and deletedLine.find('div') == None:
                deletedLine = None
            if addedLine != None and addedLine.find('div') == None:
                addedLine = None

            if deletedLine != None and addedLine != None:
                f = open("%{0}%{1}.txt".format(title, dt_string), "w")
                addedLine = str(addedLine)
                deletedLine = str(deletedLine)
                f.write(deletedLine + "\n" + addedLine)
                f.close()
                # imgkit.from_string(
                #     str(deletedLine) + str(addedLine), str(counter) + '.png')
            elif deletedLine == None and addedLine != None:
                f = open("%{0}%{1}.txt".format(title, dt_string), "w")
                addedLine = str(addedLine)

                f.write(addedLine)
                f.close()
                # imgkit.from_string(
                #     str(addedLine), str(counter) + '.png')
            elif deletedLine != None and addedLine == None:
                f = open("%{0}%{1}.txt".format(title, dt_string), "w")
                deletedLine = str(deletedLine)

                f.write(deletedLine)
                f.close()
                # imgkit.from_string(
                #     str(deletedLine), str(counter) + '.png')


while True:
    for title in titles:
        print(title)
        url = 'https://en.wikipedia.org/w/index.php?title=' + title + '&action=history'

        # Query for new revision
        req = requests.get(url, headers)
        soup = BeautifulSoup(req.content, 'lxml')

        history = soup.find(id='pagehistory')

        curr = history.find('li')

        if title not in mostRecent or curr != mostRecent[title]:
            mostRecent[title] = curr
            # create image
            createTweet(curr)
    time.sleep(3600)
