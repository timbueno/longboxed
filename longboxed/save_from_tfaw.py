import csv
import gzip
import HTMLParser
import re
import requests
import sys

from datetime import datetime

from .services import comics as _comics


AFFILIATE_ID = '782419'
DD_FILE = 'dd.gz'


def daily_download():
    print 'Downloading Daily Download'
    # daily download url and affiliate id params
    base_url = 'http://www.tfaw.com/intranet/download-8908-daily.php'
    payload = {
        'aid': AFFILIATE_ID,
        't': '',
        'z': 'gz'
    }
    # Download the file
    r = requests.get(base_url, params=payload)
    with open(DD_FILE, 'wb') as code:
        code.write(r.content)
    print '...Done'
    return


def get_comics():
    print 'Checking for comics'
    # open gzip archive and extract only comics
    with gzip.open(DD_FILE, 'rb') as f:
        # file_content = f.read()
        # f.close()
        # decoded_content = file_content.decode('iso-8859-7')
        # # encoded_content = decoded_content.encode('utf8')
        comics = []
        reader = csv.reader(f, delimiter='|')
        for item in reader:
            if item[-5] == 'Comics':
                item = [element for element in item]
                comics.append(item)
    print '...Done'
    return comics


def title_info(title):
    try:
        # Try a basic matching technique
        m = re.match(r'(?P<name>[^#]*[^#\s])\s*(?:#(?P<issue_number>(\d+))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', title).groupdict()
        # Convert issue numbers to floats
        if is_float(m['issue_number']):
            m['issue_number'] = float(m['issue_number'])
        if is_float(m['issues']):
            m['issues'] = float(m['issues'])
        m['one_shot'] = False
        other = m['other']
        # Handle multiple parenthesis matches
        if '' in other and len(other) == 1:
            other = [] # Make a fresh list
            # m['other'] = None # For consistancy
            n = re.findall(r'\s*(\(.*?\))',m['name']) # Find all parenthesis groups
            # Add all groups to other list
            if n:
                # other = []
                for match in n:
                    m['name'] = m['name'].replace(match, '')
                    other.append(match)
                m['name'] = m['name'].strip() # Clean up the name
                m['other'] = other
        if m['name'].find('One Shot') != -1:
            # Set 'One Shot' flag
            m['one_shot'] = True
            # Remove 'One Shot' from name
            m['name'] = m['name'].replace('One Shot', '')
        m['other'] = other
    except AttributeError:
        # print "Unexpected error:", sys.exc_info()
        print 'Throwing out comic!'
        m = None
    finally:
        if m:
            m['complete_title'] = title
    return m


def is_float(number):
    try: 
        float(number)
        return True
    except (ValueError, TypeError):
        return False


def add_comics_to_db():
    daily_download()
    comics = get_comics()
    parser = HTMLParser.HTMLParser()
    for q, comic in enumerate(comics):
        try:
            p = {}
            t = {}
            i = {}

            # Extract Title Info
            t_info = title_info(comic[1])
            if not t_info:
                continue

            # Publisher
            p['name'] = comic[19]

            # Title
            t['name'] = t_info['name']

            # Issue
            i['product_id'] = comic[0]
            i['issue_number'] = t_info['issue_number']
            i['issues'] = t_info['issues']
            i['other'] = t_info['other']
            i['complete_title'] = t_info['complete_title']
            i['one_shot'] = t_info['one_shot']
            i['a_link'] = re.sub('YOURUSERID', AFFILIATE_ID, comic[4])
            i['thumbnail'] = comic[5]
            i['big_image'] = comic[6]
            i['retail_price'] = float(comic[8]) if is_float(comic[8]) else None
            i['description'] = parser.unescape(comic[11])
            try:
                i['on_sale_date'] = datetime.strptime(comic[12], '%Y-%m-%d')
            except:
                i['on_sale_date'] = None
            i['genre'] = comic[13]
            i['people'] = None #### Fixme
            i['popularity'] = float(comic[16]) if is_float(comic[16]) else None
            try:
                i['last_updated'] = datetime.strptime(comic[17], '%Y-%m-%d %H:%M:%S')
            except:
                i['last_updated'] = None
            i['diamond_id'] = comic[20]
            i['category'] = comic[21]
            i['upc'] = comic[25]

            # Insert comic into collection
            _comics.insert_comic(p, t, i)

            if q % 250 == 0:
                print 'Saved %d / %d comics' % (q, len(comics))
            # if q == 50:
            #     break

        except:
            print 'SOMETHING HAPPENED', comic
            print "Unexpected error:", sys.exc_info()
            continue

    return


if __name__ == "__main__":
    add_comics_to_db()