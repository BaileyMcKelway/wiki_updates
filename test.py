# Import package
import wikipedia
# Specify the title of the Wikipedia page
wiki = wikipedia.page('National responses to the COVID-19 pandemic')
# Extract the plain text content of the page
text = wiki.content

print(text.split('===')[0])
