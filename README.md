# wiki_updates
A web scraping script that continually checks revisions made to Wikipedia articles tweeting out new revisions made that are notable(based on size of text body added to article)


# Examples
![alt text](https://i.imgur.com/wVXjGWC.png)
![alt text](https://i.imgur.com/zX2nk4N.png)

# Getting Started
Example Usage:
```
wikiTitles = [
'National_responses_to_the_COVID-19_pandemic',
'COVID-19_vaccine',
'Workplace_hazard_controls_for_COVID-19',
'COVID-19_pandemic_in_the_United_States',
'COVID-19_pandemic_in_Brazil',
'COVID-19_pandemic_in_India',
'COVID-19_pandemic_in_Russia',
'COVID-19_pandemic_in_the_United_Kingdom',
'COVID-19_pandemic_in_Iran',
]


Scraper = WikiUpdate(wikiTitles, twitter_key, twitter_secret, twitter_token, twitter_tokenSecret)
Scraper.mainFunc()
```
