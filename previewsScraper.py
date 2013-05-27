import requests
import re
import time
import string
import urlparse

from datetime import datetime
from bs4 import BeautifulSoup
from decimal import Decimal

def getComics(url="http://www.previewsworld.com/Home/1/1/71/954"):
    # Get HTML Content
    response = requests.get(url)
    # response = alp.Request(url)
    # Make soup
    soup = BeautifulSoup(response.text)
    # soup = response.souper()

    #Get the date from the top of the page
    headline = soup.find('div', class_='Headline')
    # print headline
    headlineText = headline.get_text(strip=True)
    d = re.search("([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})", headlineText)
    d = d.group(1)
    # date = time.strptime(d, "%m/%d/%Y")
    date = datetime.strptime(d, "%m/%d/%Y")

    # Find the table containing the comics
    # table = soup.find("table", {"style":"width: 100%;" ,"border": "1"})
    # print table
    found = False
    comics_table = None
    max_rows = 0
    for table in soup.findAll('table'):
        number_of_rows = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
        if number_of_rows > max_rows:
            if table.findAll(text='DARK HORSE COMICS') and table.findAll(text='IMAGE COMICS'):
                found = True
                comics_table = table
                max_rows = number_of_rows

    entries = {}
    for publisher in comics_table.findAll("td", {"colspan":"3", "align":"center"}):
        # Extract Publishers Name
        name = string.capwords(publisher.text)
        
        # Build a list to hold all books for that publisher
        books = []

        # Look for all books underneath that publisher
        tdCount = 0
        book = {}
        for cell in publisher.find_all_next():
            
            # Break between publishers and end of table
            if cell.attrs == {'colspan': '3', 'align': 'center', 'bgcolor': '#E5E7ED'}:
                break
            if cell.name == "h2":
                break
            if cell.name == "p":
                break

            # Each book consists of 3 td cells
            if cell.name == "td":
                
                tdCount = tdCount + 1

                if tdCount == 1:
                    for link in cell.findAll('a'):
                        thing = link.get('href')
                    book['link'] = thing
                    book['id'] = cell.text
                elif tdCount == 2:
                    text = re.sub('\s*(\(|\[).+$', '',cell.text)
                    book['title'] = string.capwords(text)
                elif tdCount == 3:
                    try:
                        book['priceText'] = cell.text.strip('$')
                        book['price'] = float(cell.text.strip('$'))
                    except ValueError:
                        book['priceText'] = cell.text.strip('$')
                        book['price'] = None
                
                # Prepare variables for next book
                if tdCount == 3:
                    book['date'] = date
                    book['publisher'] = name
                    book['last_updated'] = datetime.now()
                    book['image_url'] = get_image_link(book['link'])
                    books.append(book) # Add book dict to books list
                    book = {}   # instantiate a fresh book dictionary
                    tdCount = 0 # reset the td count for next book

        # Add publisher to publisher dictionary
        entries[name] = books

    return entries

def get_image_link(url='http://www.previewsworld.com/'):

    url = urlparse.urlsplit(url)
    # print url.netloc

    # Get html of comic page
    response = requests.get(url.geturl())

    # Make soup
    soup = BeautifulSoup(response.text)

    # Find image
    try:
        i = soup.find('a', {'class': 'FancyPopupImage'})
        image = i['href']
    except:
        return None

    # Construct final url of image
    imageurl = urlparse.urljoin(url.scheme+'://'+url.netloc, image)

    # Get header content and validate content is an image
    response = requests.head(imageurl)
    if response.headers['content-type'] == 'image/jpeg':
        return imageurl
    else:
        return None

if __name__ == "__main__":

    # url = "http://www.previewsworld.com/Home/1/1/71/952" # New Releases
    # url = "http://www.previewsworld.com/Home/1/1/71/954" # Upcoming Releases
    
    # entries = getComics(url)

    imageurl = get_image_link()
    print imageurl

    # Print out dictionary
    # print entries.keys()
    # for key in entries.keys():
    #     print key
    #     for book in entries[key]:
    #         print book['price']

        # print key
        # print '***************'
        # for book in entries[key]:
        #     print '%s - %s' % (book['title'], book['price'])
        #     print ''


