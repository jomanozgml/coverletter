import urllib.request
# from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

def get_page(url):
    # Opening up LinkedIn job specific page if pasted url is from searchpage
    if 'linkedin' in url and 'currentJobId' in url:
        jobId = url.split('currentJobId=')[1].split('&')[0]
        baseUrl = 'https://www.linkedin.com/jobs/view/'
        url = baseUrl + jobId

    response = urllib.request.urlopen(url)
    soup = BeautifulSoup(response, 'html.parser',
                         from_encoding=response.info().get_param('charset'))
    title = soup.title.string
    text = []
    try:
        if 'seek' in url:
            position = soup.find(attrs={"data-automation": "job-detail-title"}).text
            company = soup.find(attrs={"data-automation": "advertiser-name"}).text
            details = soup.find(attrs={"data-automation": "jobAdDetails"}).get_text(separator='\n')
            salary = soup.find(string=re.compile(r'per (annum|year|month)'))
            text = [position, company, salary, details]

        elif 'linkedin' in url:
            position = soup.find('h1').text
            company = soup.find(class_ ='topcard__flavor').text
            details = soup.find(class_ = 'description__text description__text--rich').get_text(separator='\n')
            salary = ''
            text = [position, company, salary, details]

        else:
            raise Exception("Unknown URL")
    except:
        desc = soup.find("meta", property="og:description")['content'] or ''
        tags = soup.select("p, h1, h2, h3, h4, h5, h6, ul")
        text = [item.text+'\n' for item in list(tags)]

    print('extracted using bs4')
    return title, text
