import re
import requests
import imgkit
import time
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from fuzzy_matcher import process
from datetime import datetime


class WikiUpdate:

    def __init__(self):
        self.headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

        self.titles = ['National_responses_to_the_COVID-19_pandemic',
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

        self.mostRecent = {}
        self.queue = []

    def mainFunc(self):
        while True:
            # object will be pushed to queue
            revisionAll = {}
            # Loop Titles
            for title in self.titles:
                print('TITLE', title)
                url = 'https://en.wikipedia.org/w/index.php?title=' + title + '&action=history'

                # Query for new revision
                req = requests.get(url, self.headers)
                soup = BeautifulSoup(req.content, 'lxml')
                history = soup.find(id='pagehistory')

                allRevisions = history.find_all('li')
                allRevisionsLength = len(allRevisions)

                # check = allRevisions[allRevisionsLength - 1]
                # checkFullDate = check.find(
                #     class_="mw-changeslist-date").get_text()

                mostRecentTime = None

                if title not in self.mostRecent:
                    mostRecentTime = allRevisions[allRevisionsLength - 1].find(
                        class_="mw-changeslist-date").get_text()
                else:
                    mostRecentTime = self.mostRecent[title]

                i = allRevisionsLength - 1
                startChecking = False
                while i >= 0:
                    currDate = allRevisions[i].find(
                        class_="mw-changeslist-date").get_text()
                    if mostRecentTime == currDate:
                        startChecking = True

                    if startChecking == True:
                        revisions = self.addQueue(allRevisions[i])
                        if revisions != None:
                            if title in revisionAll:
                                revisionAll[title] = revisionAll[title] + \
                                    revisions
                            else:
                                revisionAll[title] = revisions

                    i -= 1
                    # check = allRevisions[i]
                    # checkFullDate = check.find(
                    #     class_="mw-changeslist-date").get_text()

                self.mostRecent[title] = allRevisions[0].find(
                    class_="mw-changeslist-date").get_text()
                allRevisions = []
                startChecking = False

            self.queue.append(revisionAll)

            if len(self.queue) >= 5:
                self.checkDeleted()

            time.sleep(3600)

    def addQueue(self, curr):
        if self.checkSize(curr) == True:
            prevLink = curr.span.find('a', text='prev', href=True)
            currLink = curr.span.find('a', text='cur', href=True)

            if prevLink == None or currLink == None:
                return

            prevHref = 'https://en.wikipedia.org/' + prevLink['href']
            curHref = 'https://en.wikipedia.org/' + currLink['href']

            req = requests.get(prevHref, self.headers)

            soup = BeautifulSoup(req.content, 'lxml')

            # find table
            revisionId = curr['data-mw-revid']
            title = soup.find("h1", id="firstHeading").get_text().split(":")[0]
            table = soup.find('table')
            tableRows = table.find_all('tr')

            res = []
            # loop   through table rows
            for tableRow in tableRows:
                addedLine = tableRow.find(class_='diff-addedline')
                deletedLine = tableRow.find(class_='diff-deletedline')

                if addedLine != None and addedLine.find('div') == None:
                    addedLine = None

                if addedLine == None:
                    continue

                addedLineCleaned = str(addedLine)

                clean = re.compile('&lt;ref.*?&lt;/ref&gt;')
                addedLineCleaned = re.sub(clean, '', addedLineCleaned)
                addedLineCleaned = BeautifulSoup(
                    addedLineCleaned, 'html.parser')
                # CHECK IF ADDED BLOCK OR HIGHLIGHTED TEXT

                highlightedLines = addedLineCleaned.find_all(
                    'ins', {"class": "diffchange-inline"})

                pre = str(addedLine)
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                fileName = title + "_Pre" + '.txt'
                f = open(fileName, "a")
                f.write("PRE")
                f.write('\n')
                f.write("Title: " + title)
                f.write('\n')
                f.write("Date: " + dt_string)
                f.write('\n')
                f.write("ID: " + revisionId)
                f.write('\n')
                f.write('FULLTEXT: ' + pre)
                f.write('\n')
                f.write("Current Link: " + curHref)
                f.write('\n')
                f.write("Previous Link: " + prevHref)
                f.write('\n')
                f.write('\n')
                f.write('\n')
                f.close()

                maxLength = 0
                if len(highlightedLines) == 0 and deletedLine == None:
                    maxLength += len(addedLineCleaned.get_text())
                else:
                    for i in range(len(highlightedLines)):
                        highlightedLine = highlightedLines[i]
                        maxLength += len(highlightedLine.get_text())

                if maxLength <= 30:
                    continue
                # CHECK FOR SIZE OF HIGHLIGHTED TEXT

                # CREATE ARRAY FOR  OBJECT
                revision = {
                    'revisionId': revisionId,
                    'title': title,
                    'fullText': str(addedLineCleaned.get_text()),
                    'changedText': str(addedLine),
                    'curLink': curHref,
                    'prevLink': prevHref
                }
                res.append(revision)
            return res

    def checkDeleted(self):
        # CHECK IF REVERT
        checkRevisions = self.queue.pop(0)
        for title in self.titles:
            mainUrl = 'https://en.wikipedia.org/wiki/' + title
            article = requests.get(mainUrl, self.headers)
            urlsoup = BeautifulSoup(article.content, 'lxml')

            paragraphs = urlsoup.find_all('p')
            for i in range(len(paragraphs)):
                paragraphs[i] = paragraphs[i].text

            if title in checkRevisions:
                checkCurrentTitle = checkRevisions[title]
                for revision in checkCurrentTitle:
                    query = revision['fullText']
                    fuzzy = process.extract(
                        query, paragraphs, limit=3, scorer='ratio')

                    # fuzzyMatch > 50
                    if(fuzzy[0][1] > 50):
                        now = datetime.now()
                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                        fileName = title + "_Post" + '.txt'
                        f = open(fileName, "a")
                        f.write("POST")
                        f.write("Title: " + title)
                        f.write('\n')
                        f.write("Date: " + dt_string)
                        f.write('\n')
                        f.write("ID: " + revision['revisionId'])
                        f.write('\n')
                        f.write(revision['fullText'])
                        f.write('\n')
                        f.write(revision['changedText'])
                        f.write('\n')
                        f.write("Current Link: " + revision['curLink'])
                        f.write('\n')
                        f.write("Previous Link: " + revision['prevLink'])
                        f.write('\n')
                        f.write("Fuzzy: " + fuzzy[0][0])
                        f.write('\n')
                        f.write('\n')
                        f.write('\n')
                        f.close()

    def checkSize(self, curr):
        diffBytes = curr.find_all(
            ['span', 'strong'], class_='mw-diff-bytes', dir='ltr')[0]

        if diffBytes:
            size = diffBytes.get_text()
            size = re.sub('[+-,]', '', size)
            return int(size) >= 300
        else:
            return


Scraper = WikiUpdate()

Scraper.mainFunc()
