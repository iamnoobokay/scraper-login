import concurrent.futures
import threading
import time
from bs4 import BeautifulSoup
import http.cookiejar
import requests
import mechanize
import csv

#defining thread###################################
thread_local = threading.local()


#function to create thread session#################
###################################################
def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

############ END OF get_session#####################
####################################################



#function to visit each site########################
####################################################

def download_site(url):
    print("scraping")
    #open csv and write the column names
    with open('data.tsv', 'a',) as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', lineterminator='\n')

        #open link
        br.open(url)

        #get soup
        outputSoup=BeautifulSoup(br.response(),'html.parser')

        #get date
        date_result = outputSoup.find("time",{"class":"posting_timestamp"})
        date = date_result.text.strip() if date_result else "N/A"

        #get name
        name_result = outputSoup.find("span",{"class":"pseudonym"})
        name = name_result.text.strip() if name_result else "N/A"

        #get title
        title_result = outputSoup.find("h1",{"class":"thread_title"}).find("a")
        title = title_result.text.strip() if title_result else "N/A"
        
        #get_body
        body_result = outputSoup.find("div",{"class":"bbcode_v1"})
        body_result_p = body_result.findAll("p")
        body_result_blockquote = body_result.findAll("blockquote",{"class":"forum-blockquote"})
        body = ""
        if(len(body_result_p)>=1):
            for paragraph in body_result_p:
                paragraph=paragraph.text.strip()
                body = body+paragraph

        if(len(body_result_blockquote)>=1):
            for blockquote in body_result_blockquote:
                paragraphs = blockquote.findAll("p")
                for para in paragraphs:
                    body = body+para.text.strip()

        # write data to csv
        writer.writerow([date, name, title, body])

############ END OF download_sites##################
####################################################



########function to call download site with threads##
#####################################################

def download_all_sites(links):
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(download_site, links)

###########END OF download_all_sites#################
#####################################################



#############MAIN FUNCTION###########################
#####################################################

if __name__ == "__main__":
    #Code for login
    cj = http.cookiejar.CookieJar()
    br = mechanize.Browser()

    #bypass robots.txt
    br.set_handle_robots(False)
    br.set_cookiejar(cj)

    #open login page
    br.open("https://www.heise.de/sso/login/")

    #get login form
    for form in br.forms():
        if form.attrs['class'] == 'a-form':
            br.form = form
            break

    #set username
    br.form['username'] = 'lunokhod@protonmail.ch'
    #set password
    br.form['password'] = 'Titanium22'
    #submit
    br.submit()

    #list of links
    links = []

    #open first page
    br.open('https://www.heise.de/forum/my-postings/')
    soup = BeautifulSoup(br.response(),'html.parser')
    #links that are in first page
    first_page_links = soup.findAll("a",{"class":"posting_written_by_user_642562"})

    for link in first_page_links:
        links.append(link['href'])

    #Scrape links from second to page 87(this has not been threaded)
    for i in range(2,3):
        print("Scraping links from page: "+str(i))
        currentLink = 'https://www.heise.de/forum/my-postings/page-'+str(i)+'/'
        br.open(currentLink)
        nsoup=BeautifulSoup(br.response(),'html.parser')
        otherLinks = nsoup.findAll("a", {"class": "posting_written_by_user_642562"})
        
        for olinks in otherLinks:
            links.append(olinks['href'])

    #write heading for csv
    with open('data.tsv', 'w',) as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', lineterminator='\n')
        writer.writerow(['Date', 'Name', 'Title', 'Body'])

    #start time of threading
    start_time = time.time()

    #calling function
    download_all_sites(links)

    #duration
    duration = time.time() - start_time
    print(f"Scraped {len(links)} in {duration} seconds")

################END OF MAIN################################
###########################################################