import re
import requests
import imgkit
from bs4 import BeautifulSoup
from urllib.request import urlopen


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


def createTweet(curr):
    diffBytes = curr.find('span', class_='mw-diff-bytes', dir='ltr')

    if diffBytes:
        size = diffBytes.get_text()
    else:
        return
    print(size)
    if size and abs(int(size)) >= 100:
        link = curr.span.find('a', href=True)
        href = 'https://en.wikipedia.org/' + link['href']

        req = requests.get(href, headers)
        soup = BeautifulSoup(req.content, 'html.parser')

    # find table
        table = soup.find('table')
        tableRows = table.find_all('tr')

        # loop through table rows
        counter = 0
        for tableRow in tableRows:
            deletedLine = tableRow.find(class_='diff-deletedline')
            addedLine = tableRow.find(class_='diff-addedline')
            if deletedLine != None and deletedLine.find('div') == None:
                deletedLine = None
            if addedLine != None and addedLine.find('div') == None:
                addedLine = None

            if deletedLine != None and addedLine != None:
                imgkit.from_string(
                    str(deletedLine) + str(addedLine), str(counter) + '.png')
            elif deletedLine == None and addedLine != None:
                imgkit.from_string(
                    str(addedLine), str(counter) + '.png')
            elif deletedLine != None and addedLine == None:
                imgkit.from_string(
                    str(deletedLine), str(counter) + '.png')

            counter += 1


while True:
    for title in titles:
        print(title)
        url = 'https://en.wikipedia.org/w/index.php?title=' + title + '&action=history'

        # Query for new revision
        req = requests.get(url, headers)
        soup = BeautifulSoup(req.content, 'html.parser')

        history = soup.find(id='pagehistory')

        curr = history.find('li')

        if title not in mostRecent or curr != mostRecent[title]:
            mostRecent[title] = curr
            # create image
            createTweet(curr)
