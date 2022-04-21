from bs4 import BeautifulSoup
import urllib.request

def import_doc(wiki_link):
    url = wiki_link
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page,'html.parser')
    t = soup.html.body.table.tbody
    wiki_title = soup.html.head.title.text.rstrip()
    print(f'    <!-- From {wiki_title}: {wiki_link} -->')
    trs = list(filter(lambda x: x.name == 'tr', t.children))
    header, *rows = trs
    cols = list(map(lambda x: x.text.rstrip().replace('\xa0', ' '), filter(lambda x: x.name == 'th', header.children)))
    if (['IATA', 'ICAO', 'Airport name', 'Location served', 'Time', 'DST'] != cols) and (['IATA', 'ICAO', 'Airport name', 'Location served'] != cols):
        assert False, f"Columns didn't match for {wiki_link}"
    rows = filter(lambda x: x.th == None, rows)
    for r in rows:
        iata, icao, name, loc, *_ = list(map(lambda x: x.text.rstrip().replace('\xa0', ' '), filter(lambda x: x.name == 'td', r.children)))
        print(f"""    <ar>
      <k>{iata}</k>
      {f"<k>{icao}</k>" if icao != "" else ""}
      <def>
        <deftext>
          {name} <categ>(<kref idref="IATA_airport_code_1">IATA airport codes</kref>)</categ>
          <def>
            <deftext>
              {loc}
              <iref href="{wiki_link}">{wiki_title}</iref>
            </deftext>
          </def>
        </deftext>
      </def>
    </ar>""")


print('    <ar><k id="IATA_airport_code_1">IATA airport codes</k><def><deftext>IATA airport codes</deftext></def></ar>')


for l in range(ord('A'), ord('Z')):
   link = f'https://en.wikipedia.org/wiki/List_of_airports_by_IATA_airport_code:_{chr(l)}'
   import_doc(link)