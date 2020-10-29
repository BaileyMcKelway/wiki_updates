import tweepy

key = 'NSkKvBJI7UHeUdWAlvsYknQEm'
secret = 'oBD3k0uczP5nkTcVnNkmKkuF0tel4vtAzYEHQHSj7gHRdmP1kG'

token = '1321211489278173186-9GrEzJ3CT1XKEhS1wEav2FiFBAVCKj'
tokenSecret = '2cqLHWi9vE6hDeLOKobZFDD3h5NnUIR24biOCTxDVbLAu'

auth = tweepy.OAuthHandler(key, secret)
auth.set_access_token(token, tokenSecret)

api = tweepy.API(auth)
api.update_with_media(
    './out.jpg', 'https://en.wikipedia.org//w/index.php?title=National_responses_to_the_COVID-19_pandemic&diff=985417966&oldid=985052321')
