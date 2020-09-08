import re
from xml.sax import saxutils as su

test = """<td class="diff-deletedline"><div>On 23 March, a national 21-day lockdown was announced by President Ramaphosa to begin on 26 March to 16 April.&lt;ref name="Lockdown" /&gt; By 24 March all nine provinces had confirmed cases, with the first cases in the [[Northern Cape]] and [[North West (South African province)|North West]] announced.&lt;ref&gt;{{Cite web|url=https://www.health24.com/Medical/Infectious-diseases/Coronavirus/coronavirus-morning-update-sa-prepares-for-lockdown-as-confirmed-cases-hit-402-20200324|title=Coronavirus morning update: SA prepares for lockdown as confirmed cases hit 402|date=24 March 2020|website=health24|accessdate=26 April 2020}}&lt;/ref&gt;<del class="diffchange diffchange-inline"> </del> The country's first death was announced on 27 March.&lt;ref name="gov.za1170"/&gt;</div></td> <td class="diff-addedline"><div>On 23 March, a national 21-day lockdown was announced by President Ramaphosa to begin on 26 March to 16 April.&lt;ref name="Lockdown" /&gt; By 24 March all nine provinces had confirmed cases, with the first cases in the [[Northern Cape]] and [[North West (South African province)|North West]] announced.&lt;ref&gt;{{Cite web|url=https://www.health24.com/Medical/Infectious-diseases/Coronavirus/coronavirus-morning-update-sa-prepares-for-lockdown-as-confirmed-cases-hit-402-20200324|title=Coronavirus morning update: SA prepares for lockdown as confirmed cases hit 402|date=24 March 2020|website=health24|accessdate=26 April 2020}}&lt;/ref&gt; The country's first death was announced on 27 March.&lt;ref name="gov.za1170"/&gt;</div></td>"""

test = su.unescape(test)

print(test)
# Remove and store ref for test
