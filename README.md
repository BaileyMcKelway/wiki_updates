# wiki_updates
A web scraping script that continually checks revisions made to Wikipedia articles tweeting out new revisions made that are notable(based on size of text body added to article)


# Examples
![alt text](https://i.imgur.com/wVXjGWC.png)
![alt text](https://i.imgur.com/zX2nk4N.png)

# Getting Started


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
'Severe_acute_respiratory_syndrome_coronavirus_2',
'Coronavirus',
'COVID-19_pandemic',
'Coronavirus_disease_2019',
'Coronavirus_disease',
'COVID-19_recession',
'Misinformation_related_to_the_COVID-19_pandemic',
'COVID-19_drug_development',
'Impact_of_the_COVID-19_pandemic_on_science_and_technology',
'Impact_of_the_COVID-19_pandemic_on_the_environment',
'Impact_of_the_COVID-19_pandemic_on_politics',
'Financial_market_impact_of_the_COVID-19_pandemic',
'Impact_of_the_COVID-19_pandemic_on_social_media',
'Mental_health_during_the_COVID-19_pandemic',
'Human_rights_issues_related_to_the_COVID-19_pandemic'
]


Scraper = WikiUpdate(wikiTitles, twitter_key, twitter_secret, twitter_token, twitter_tokenSecret)
Scraper.mainFunc()
```
