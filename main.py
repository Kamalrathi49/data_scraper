from typing import ItemsView
import requests
from bs4 import BeautifulSoup
from requests.sessions import session
import pandas as pd
from tqdm import tqdm
import csv

res = requests.get("https://ep70.eventpilotadmin.com/web/page.php?page=Session&project=AAIC19&id=5172&filterUrn=urn%3Aeventpilot%3Aall%3Aagenda%3Afilter%3Acategoryid%3DClinical+%28neuropsychiatry+and+behavioral+neurology%29")
soup = BeautifulSoup(res.text, "html.parser")
links = soup.select('.catimg')

def get_pages_link(links):
    link_list = []
    for idx, item in enumerate(links):
        links = item.getText()
        href = item.get('href', None)
        link_list.append('https://ep70.eventpilotadmin.com/web/'+href)
    return link_list

def scrapper(link):
    resp= requests.get(link)
    data = BeautifulSoup(resp.text, "html.parser")
    session_title = data.select(".session_detail_title_708 span")[0].getText()
    session_day = data.find_all("div", class_="session_detail_day")
    session_time = session_day[0].getText().replace('\n','').replace('\t','')
    session_date = session_day[1].getText().replace('\n','').replace('\t','').replace('\xa0','')
    session_author = data.select("div#session_detail_description b", Text="Author Block")[-1].getText()
    for strong_tag in data.select("div#session_detail_description b", Text="Author Block"):
        authors_affiliation = strong_tag.next_sibling
    session_category = data.find_all("div", class_="filter_value")
    category = session_category[0].getText()
    sub_category = session_category[-1].getText()
    session_location =  data.select(".ui-li-aside")[1]
    location = session_location.getText().split("\n")
    location, abstract = location[0] , location[1]
    abstract_text = data.select("div.mediatextwrapper h1.list_cell_title span")[0].getText()
    session_abstract_title = data.select(".session_title")[0].getText()
    scraped_data = {'#Abstract': abstract, 'Abstract Title': session_title, 'Date': session_date, "Time": session_time, 'Location': location, 'URL':link ,"Authors": session_author, "Author's Affiliations": authors_affiliation,'Abstract Text': abstract_text, 'Category': category, 'Sub-Category': sub_category, "Abstract Title": session_abstract_title  }
    return scraped_data

final_scrapped_data = []
for item in tqdm(get_pages_link(links)):
    final_scrapped_data.append(scrapper(item))
    
field_names = ['#Abstract', 'Abstract Title', 'Date', 'Time', 'Location','URL', 'Authors', "Author's Affiliations", 'Abstract Text', 'Category', 'Sub-Category', 'Session Title']
import io
with io.open('data.csv', 'w', encoding="utf-8", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = field_names)
    writer.writeheader()
    writer.writerows(final_scrapped_data)