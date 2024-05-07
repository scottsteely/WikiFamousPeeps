"""
I'm going to comment this, but I'm tired.


"""

from SPARQLWrapper import SPARQLWrapper2
import json
import urllib.request
import wikipedia
import os
import glob
import random
import time
from tqdm import tqdm
from datetime import datetime
from textwrap import fill
from wand.image import Image


now = datetime.today().strftime("%Y")
start_time = time.time()


def str_time_prop(start, end, time_format, prop):
    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))
    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, "%Y", prop)


random_year = int(random_date("1960", now, random.random()))

peeps_year_born = random_year
peep_pic_size = 200
Peeps_list = []

print(("\n Getting peeps born on {}").format(random_year))


class Peep:

    def __init__(
        self,
        person,
        article_link,
        descp,
        wiki_pageid="",
        wiki_title="",
        wiki_extract="",
        wiki_image="",
        wiki_image_thumb="",
    ):
        self.name = person
        self.article_link = article_link
        self.desc = descp
        self.pageid = wiki_pageid
        self.title = wiki_title
        self.extract = wiki_extract
        self.image = wiki_image
        self.image_thumb = wiki_image_thumb


def wiki_blurb(person, article_link_title):
    urlData = (
        "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext=1&titles={}"
    ).format(article_link_title)

    webURL = urllib.request.urlopen(urlData)
    data = webURL.read()
    JSON_object = json.loads(data.decode("utf-8"))

    for key in JSON_object["query"]["pages"]:
        page_id = key

    page_title = JSON_object["query"]["pages"][page_id]["title"]
    page_extract = JSON_object["query"]["pages"][page_id]["extract"]

    sentance1 = page_extract.partition(".")
    sentance2 = sentance1[2].partition(".")

    blurb = sentance1[0] + "." + sentance2[0] + "."
    person.pageid = page_id
    person.title = page_title
    person.extract = blurb


sparql = SPARQLWrapper2("https://query.wikidata.org/sparql")
SuperSparkleQuery = (
    """
    SELECT DISTINCT ?item WHERE {{
      ?item wdt:P31 wd:Q5;
            wdt:P18 ?pic;
            #wdt:P54 ?team;
            wikibase:sitelinks ?sitelinks;
            wdt:P569 ?dateOfBirth. hint:Prior hint:rangeSafe true.
      FILTER((("{}-00-00"^^xsd:dateTime <= ?dateOfBirth && ?dateOfBirth < "{}-00-00"^^xsd:dateTime )&& ?sitelinks>20))
      FILTER NOT EXISTS {{?item wdt:P54 ?o}}
    }}
    ORDER BY RAND()
    LIMIT 10
    """
).format(peeps_year_born, (peeps_year_born + 1))

sparql.setQuery(SuperSparkleQuery)

print("\n Querying WikiData with custom SPARQL payload")

progression_bar = tqdm(sparql.query().bindings)
for result in progression_bar:
    # progression_bar.set_description("Getting peep « %s »" % str(person.name))

    wiki_Q = (f"{result['item'].value}").lstrip("http://www.wikidata.org/entity/")
    urlData = (
        "https://www.wikidata.org/w/api.php?action=wbgetentities&ids={}&languages=en&props=descriptions|sitelinks%2Furls&sitefilter=enwiki&format=json"
    ).format(wiki_Q)
    webURL = urllib.request.urlopen(urlData)
    data = webURL.read()
    JSON_object = json.loads(data.decode("utf-8"))

    article_link = JSON_object["entities"][wiki_Q]["sitelinks"]["enwiki"]["url"]
    descp = JSON_object["entities"][wiki_Q]["descriptions"]["en"]["value"]
    person = article_link.lstrip("https://en.wikipedia.org/wiki/")
    person = Peep(person, article_link, descp)
    Peeps_list.append(person)


print("\n Now getting the corrisponding Wikipedia article and info")

progression_bar = tqdm(Peeps_list)
for person in progression_bar:
    progression_bar.set_description("Downloading article « %s »" % str(person.name))
    wiki_blurb(person, person.name)
    page = wikipedia.page(pageid=person.pageid)
    person.image = page.images[0]

    urlData = (
        "https://en.wikipedia.org/w/api.php?action=query&titles={}&prop=pageimages&format=json&pithumbsize={}"
    ).format(person.name, peep_pic_size)
    webURL = urllib.request.urlopen(urlData)
    data = webURL.read()
    JSON_object = json.loads(data.decode("utf-8"))

    for key in JSON_object["query"]["pages"]:
        page_id = key

    person.image_thumb = JSON_object["query"]["pages"][page_id]["thumbnail"]["source"]


#### clear the folder for the pictures
# files = glob.glob("./wiki_pics/*")
# for f in files:
#    os.remove(f)

print("\n Get the thumbnail, convet to sixel, make the txt file")
progression_bar = tqdm(Peeps_list)

for person in progression_bar:

    pic_save_loc = ("./wiki_pics/{}.jpg").format(person.title)
    urllib.request.urlretrieve(person.image_thumb, pic_save_loc)

    with Image(filename=pic_save_loc) as img:
        img.format = "sixel"
        img.save(filename="./wiki_pics/" + person.title + ".sixel")

    snipet = ("./wiki_pics/{}.txt").format(person.title)
    snipet_body = (
        """
{}

{}
{}
        """
    ).format(
        person.title,
        person.desc,
        person.extract,
    )

    snipet_body = fill(
        snipet_body,
        width=60,
        fix_sentence_endings=True,
    )
    with open(snipet, "w") as file:
        file.write(snipet_body)

# clean up
files = glob.glob("./wiki_pics/*.jpg")
for f in files:
    os.remove(f)

print("\n \n Process Complete in", round((time.time() - start_time), 2), "seconds.")
