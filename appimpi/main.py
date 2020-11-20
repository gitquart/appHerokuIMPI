from selenium import webdriver
import chromedriver_autoinstaller
import time
import requests 
from selenium.webdriver.chrome.options import Options
import os
import utils as tool
import cassandraSent as bd

chromedriver_autoinstaller.install()
download_dir='/app/Downloadimpi'
#Erase every file in download folder at the beginning to avoid mixed files
print('Checking if download folder exists...')
isdir = os.path.isdir(download_dir)
if isdir==False:
    print('Creating download folder...')
    os.mkdir(download_dir)
print('Download directory created...')
for file in os.listdir(download_dir):
    os.remove(download_dir+'/'+file)

print('Download folder empty...')
#Set options for chrome
options = Options()

profile = {"plugins.plugins_list": [{"enabled": True, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": download_dir , 
               "download.prompt_for_download": False,
               "download.directory_upgrade": True,
               "download.extensions_to_open": "applications/pdf",
               "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
               }           

options.add_experimental_option("prefs", profile)

browser=webdriver.Chrome(options=options)

lsInfo=bd.getPageAndTopic()
StartID=int(lsInfo[1])
EndID=14000
while(StartID<=EndID):
    #This iteration gets each file
    urlExp="https://vidoc.impi.gob.mx/visor?usr=SIGA&texp=SI&tdoc=E&id=MX/a/2015/00"+str(StartID)
    response= requests.get(urlExp)
    status= response.status_code
    if status==200:
        browser.get(urlExp)
        time.sleep(1)
        alerta=browser.find_element_by_xpath('//*[@id="divAlertas"]/div/strong')
        if alerta is None:
            print('No alert of NO FILE found...all good')
            #Check if the url (File= expedient) has a table, if table is  none, then skip til next url
            table=browser.find_element_by_xpath('//*[@id="MainContent_gdDoctosExpediente"]')
            if table is not None:
                #Get nomber of rows of the table
                rows = browser.find_elements_by_xpath("//*[@id='MainContent_gdDoctosExpediente']/tbody/tr")
                nRows=len(rows)+1
                for trow in range(1,nRows):
                    tool.processRows(browser,trow)
    
                print('-------------Page done-------------')
                StartID=StartID+1
                bd.updatePage(StartID)
            else:
                print('No table found...')
        else:
            print('------No existe el expediente solicitado------')
            StartID=StartID+1
            bd.updatePage(StartID)

    else:
        print('The IMPI site is not responding....')          