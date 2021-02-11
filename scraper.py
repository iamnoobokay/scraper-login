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

#Scrape links from first page
br.open('https://www.heise.de/forum/my-postings/')
soup = BeautifulSoup(br.response(),'html.parser')

links = soup.findAll("a",{"class":"posting_written_by_user_642562"})

#Scrape links from second to page 87(Please change it to a lower value too slow)
for i in range(2,88):
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
        date = outputSoup.find("time",{"class":"posting_timestamp"}).text.strip()

        #get name
        name = outputSoup.find("span",{"class":"pseudonym"}).text.strip()

        #get title
        title = outputSoup.find("h1",{"class":"thread_title"}).find("a").text.strip()

        #get_body
        body = outputSoup.find("div",{"class":"bbcode_v1"}).find("p").text.strip()

        #write data to csv
        writer.writerow([date, name, title, body])

        print(str(j)+' total posts written to csv')

        #increment counter
        j=j+1

#close file
writer.close()

    
