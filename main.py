"""For fetching news from dainik bhaskar into epub format"""

from datetime import date
TODAY = date.today()

LINKS = {"National": "https://www.bhaskar.com/rss-v1--category-1061.xml",
              "International": "https://www.bhaskar.com/rss-v1--category-1125.xml",
              "Business": "https://www.bhaskar.com/rss-v1--category-1051.xml",
              "Sports": "https://www.bhaskar.com/rss-v1--category-1053.xml",
              "Magazine": "https://www.bhaskar.com/rss-v1--category-1057.xml",
              "Original": "https://www.bhaskar.com/rss-v1--category-4587.xml",
              "Editorial": "https://www.bhaskar.com/rss-v1--category-1944.xml"
              }

def valid_date(art_date, today):
    if today.year > art_date["year"]:
        if art_date["day"] == 31:
            return True
    else:
        if today.month > art_date["month"]:
            if art_date["month"]==2:
                if art_date["day"]>=28:
                    return True
            else:
                if art_date["day"]>=30:
                    return True
        else:
            if today.day - art_date["day"] <=1:
                return True
    return False

def get_relevant_feed(URL):
    page = requests.get(URL)
    data = xmltodict.parse(page.content)
    ch = data['rss']['channel']
    item = ch['item'] # list of elements with keys == title, link, guid, atom:link, description, pubDate, media:content
    titles = []
    contents = []
    for elt in item:
        art_date = elt["pubDate"].split()
        ref_dict = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
        relevant_date = {}
        try:
            relevant_date["day"] = int(art_date[1])
            relevant_date["month"] = int(ref_dict[art_date[2]])
            relevant_date["year"] = int(art_date[3])
            # print(relevant_date)
        except:
            print("Couldn't convert date of article")
        
        add_article = True
        if relevant_date:
            add_article = valid_date(relevant_date, TODAY)
            # print(relevant_date, add_article)
        
        if add_article:
            titles.append(elt['title'])
            contents.append(elt['description'])
            # print("*")
    
    return titles, contents


import requests
import xmltodict
from ebooklib import epub

data = {}
for key in LINKS:
    key_title, key_content = get_relevant_feed(LINKS[key])
    data[key] = [key_title,key_content]
print(data.keys())
# print(data)

book = epub.EpubBook()
# set metadata
book.set_identifier(f"id_{TODAY}")
book.set_title(f"Dainik Bhaskar on {TODAY}")
book.set_language("en")
book.add_author("Dainik_Bhaskar")

# create chapter
c1 = epub.EpubHtml(title="Intro", file_name="chap_01.xhtml", lang="en")
mystr = ""
for key in data:
    titles, contents = data[key][0], data[key][1]
    mystr = f"{mystr}<h1>{key}</h1>"
    for i in range(len(titles)):
        mystr = f"{mystr}<h3>{titles[i]}</h3><p>{contents[i]}</p>"
    # print(mystr)

c1.content = (mystr)



# add chapter
book.add_item(c1)

# # define Table Of Contents
# book.toc = (
#     epub.Link("chap_01.xhtml", "Introduction", "intro"),
#     (epub.Section("Simple book"), (c1,)),
# )


# add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

# define CSS style
style = "BODY {color: white;}"
nav_css = epub.EpubItem(
    uid="style_nav",
    file_name="style/nav.css",
    media_type="text/css",
    content=style,
)

# add CSS file
book.add_item(nav_css)

# basic spine
book.spine = ["nav", c1]

# write to the file
epub.write_epub(f"Dainik_Bhaskar_{TODAY}.epub", book, {})
