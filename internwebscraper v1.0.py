from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import yaml
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.oauth2.credentials import Credentials



driver = webdriver.Chrome() 
listings = []
seen_listings = set()

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

def loadYaml(): #load yaml file containing credentials
    with open(r'C:\Users\Thanatos\settings.yml', 'r') as f:
    # Rest of your code here

        credentials = yaml.safe_load(f)
    return credentials

def uploadToDrive(): #upload csv
    credentials = loadYaml() #load yaml file containing credentials
    client_config = credentials['client_config'] 
    token = credentials['save_credentials_file'] 

    creds = Credentials.from_authorized_user_info(client_config, token=token) 
    drive = creds.create_delegated('waluigi.wolf@gmail.com') #drive account to upload to

    upload = 'internships.csv' #internship csv file
    files = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList() #get list of files in drive

    for file in files:
        if file['title'] == upload: #just update the file if it already exists
            fileID = file['id'] 
            file1 = drive.CreateFile({'id': fileID}) 
            file1.SetContentFile(upload) #set content to the csv file
            file1.Upload() #upload file 
            return #exit
        
        
        gfile = drive.CreateFile({'parents': [{'id':'1_Exm7DlS3LzLwO_ByaKWskdA5gCu93ag'}]}) #if the file doesnt exist create it
        gfile.SetContentFile(upload) #set content to the csv file
        gfile.Upload()  #upload file





def getJora(listings):
    start = 1 #Jora only has 2 pages of internships
    end = 2
   

    for page in range(start, end + 1): #loop through pages
        url = f"https://au.jora.com/Computer-Science-Internship-jobs-in-Melbourne-VIC?page={page}"
        driver.get(url)
        data = driver.page_source
        soup = BeautifulSoup(data, 'html.parser') #parse html for listings

        for listing in soup.find_all('div', class_='job-card'): #for each listing check elements
            title_element = listing.find('h3', class_='job-title')
            title = title_element.text.strip() if title_element else None

            company_element = listing.find('span', class_='job-company')
            company = company_element.text.strip() if company_element else None

            location_element = listing.find('a', class_='job-location')
            location = location_element.text.strip() if location_element else None

            abstract_element = listing.find('div', class_='job-abstract')
            abstract = abstract_element.text.strip() if abstract_element else None

            date_element = listing.find('span', class_='job-listed-date')
            date = date_element.text.strip() if date_element else None


            internship = { #dict to store listings
             'title': title,
             'company': company,
             'location': location,
             'abstract': abstract,
             'date': date,
         
         }

            listings.append(internship) #finallly append to list

    return listings

def getGradConnection(listings): #get gradconnection listings

    #only one page of listings on gradconnection so no need to loop
    driver.get("https://au.gradconnection.com/internships/computer-science/melbourne/")
    values = driver.page_source
    grad_soup = BeautifulSoup(values, 'html.parser')

    for listing in grad_soup.find_all('div', class_='campaign-box'):
        title_element = listing.find('h3')
        title = title_element.text.strip() if title_element else None

        company_element = listing.find('div', class_='box-employer-name')
        company = company_element.text.strip() if company_element else None

        location_element = listing.find('div', class_='location-name')
        location = location_element.text.strip() if location_element else None

        abstract_element = listing.find('p', class_='box-description-para')
        abstract = abstract_element.text.strip() if abstract_element else None

        
        date = "Not retreivable from GradConnection at this time"

        internship = {
            'title': title,
            'company': company,
            'location': location,
            'abstract': abstract,
            'date': date
        }

        listings.append(internship)

    return listings

#broken atm
#def getProsple(listings):
    driver.get("https://au.prosple.com/search-jobs?locations=9692%2C9692%7C9699%2C9692%7C9699%7C24329&opportunity_types=2&from_seo=1&content=internships-in-melbourne-australia&sort=newest_opportunities%7Cdesc&study_fields=502")
    data = driver.page_source
    soup = BeautifulSoup(data, 'html.parser')

    for listing in soup.find_all('section', class_='sc-dRPiIx'):
        section = listing.find('div', class_='sc-hYZPRl')
        if section is None:
            continue

        title_element = section.find('h6', class_='sc-fmlJLJ')
        title = title_element.get_text(strip=True) if title_element else ''

        company_element = section.find('p', class_='sc-cbDGPM')
        company = company_element.text.strip() if company_element else None

        location_element = section.find('p', class_='sc-irlOZD')
        location = location_element.text.strip() if location_element else None

        job_listing = {
            'Ritle': title,
            'Company': company,
            'Location': location
        }

        listings.append(job_listing)

    return listings


def formatData(listings): #format data into a dataframe for csv
 df = pd.DataFrame(listings) 
 column_order = ['title', 'company', 'location', 'abstract', 'date'] #set columns
 df = df[column_order] 
 df['location'] = df['location'].str.split().str[0] #Only want Melbourne not Melbourne, Victoria and others
 df['location'].fillna('Not listed', inplace=True) #fill empty locations with not listed
 df = df.rename(columns=lambda x: x.capitalize()) #set column names to be capitalised, don't want to change other code so this is a workaround
 return df

def updateCSV(df): 
    df.to_csv('internships.csv', index=False) #create an updated csv file


def DisplayData(df): #display data in a table
    print(df)
 
def main(listings):
    getJora(listings)
    getGradConnection(listings)
    #getProsple(listings) Prosple not allowing scraping and private api
    df = formatData(listings)
    updateCSV(df)
    DisplayData(df)
    
def upload(df): #yaml file and upload to drive not functional
    updateCSV(df)
    loadYaml()
    uploadToDrive()

main(listings)

 #add more websites
 #add functionality to mark jobs as seen
 #add links to job postings in csv