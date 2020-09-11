import re
import requests
import imgkit
import time
import sys
from bs4 import BeautifulSoup
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
queue = []


def checkSize(curr):
    diffBytes = curr.find('span', class_='mw-diff-bytes', dir='ltr')

    if diffBytes:
        size = diffBytes.get_text()
        return abs(int(size)) >= 300
    else:
        return


def addQueue(curr):

    if checkSize(curr) == True:

        prevLink = curr.span.find('a', text='prev', href=True)
        currLink = curr.span.find('a', text='cur', href=True)

        if prevLink == None or currLink == None:
            return

        prevHref = 'https://en.wikipedia.org/' + prevLink['href']
        curHref = 'https://en.wikipedia.org/' + currLink['href']

        req = requests.get(prevHref, headers)

        soup = BeautifulSoup(req.content, 'lxml')

        # find table
        revisionId = curr['data-mw-revid']
        title = soup.find("h1", id="firstHeading").get_text().split(":")[0]
        table = soup.find('table')
        tableRows = table.find_all('tr')

        res = []
        # loop   through table rows
        for tableRow in tableRows:
            deletedLine = tableRow.find(class_='diff-deletedline')
            addedLine = tableRow.find(class_='diff-addedline')
            if deletedLine != None and deletedLine.find('div') == None:
                deletedLine = None
            if addedLine != None and addedLine.find('div') == None:
                addedLine = None

            if addedLine == None:
                continue

            # changedText = addedLine.find_all(class_="diffchange-inline")

            # CREATE ARRAY FOR  OBJECT
            revision = {
                'revisionId': revisionId,
                'title': title,
                'fullText': addedLine,
                'changedText': 'changedText',
                'curLink': curHref,
                'prevLink': prevHref
            }

            res.append(revision)
        return res


while True:
    revisionAll = {}
    for title in titles:
        print(title)
        url = 'https://en.wikipedia.org/w/index.php?title=' + title + '&action=history'

        # Query for new revision
        req = requests.get(url, headers)
        soup = BeautifulSoup(req.content, 'lxml')

        history = soup.find(id='pagehistory')

        allRevisions = history.find_all('li')

        allRevisionsLength = len(allRevisions)

        check = allRevisions[allRevisionsLength - 1]
        checkFullDate = check.find(
            class_="mw-changeslist-date").get_text()

        mostRecentTime = None

        if title not in mostRecent:
            mostRecentTime = allRevisions[0].find(
                class_="mw-changeslist-date").get_text()
        else:
            mostRecentTime = mostRecent[title]

        i = allRevisionsLength - 1
        startChecking = False

        while i >= 0:
            if mostRecentTime == checkFullDate or title not in mostRecent:
                startChecking = True

            if startChecking == True:
                revisions = addQueue(check)
                print(revisions)
                if title in revisionAll:
                    revisionAll[title] = revisionAll[title].append(revisions)
                else:
                    revisionAll[title] = []
                    revisionAll[title].append(revisions)

            i -= 1
            check = allRevisions[i]
            checkFullDate = check.find(class_="mw-changeslist-date").get_text()

        mostRecent[title] = allRevisions[0].find(
            class_="mw-changeslist-date").get_text()

        allRevisions = []
        startChecking = False

    print(mostRecent)
    # if len(queue) == 5:
    #     CHECK IF REVERT
    #         IF NOT TWEET

    queue.append(revisionAll)
    print(queue)
    time.sleep(3600)
