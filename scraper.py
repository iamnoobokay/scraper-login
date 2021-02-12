#Imports
from bs4 import BeautifulSoup
import http.cookiejar
import requests
import mechanize
import csv

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

Scrape links from first page
br.open('https://www.heise.de/forum/my-postings/')
soup = BeautifulSoup(br.response(),'html.parser')

links = soup.findAll("a",{"class":"posting_written_by_user_642562"})

# links = []

#Scrape links from second to page 87(Please change it to a lower value too slow)
for i in range(17,51):
    print("Scraping links from page: "+str(i))
    currentLink = 'https://www.heise.de/forum/my-postings/page-'+str(i)+'/'
    br.open(currentLink)
    nsoup=BeautifulSoup(br.response(),'html.parser')
    otherLinks = nsoup.findAll("a", {"class": "posting_written_by_user_642562"})
    
    for olinks in otherLinks:
        links.append(olinks)

#List to store data
data_to_store=[]

#post visits counter
j=1

#open csv and write the column names
with open('data.csv', 'w',) as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Date', 'Name', 'Title', 'Body'])

    #loop to visit links
    for link in links:
        print("visiting post: "+str(j))

        #open link
        br.open(link['href'])

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
        body_p = body_result.find("p") if body_result else "N/A"
        if body_p != "N/A":
            body = body_p.text.strip()
        else:
            body = "N/A"

        #write data to csv
        writer.writerow([date, name, title, body])

        print(str(j)+' total posts written to csv')

        #increment counter
        j=j+1

#close file
# writer.close()

    
