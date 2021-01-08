from selenium import webdriver
import chromedriver_autoinstaller
import time
import requests 
from selenium.webdriver.chrome.options import Options
import os
import utils as tool
import cassandraSent as bd
from InternalControl import cInternalControl

objControl=cInternalControl()
download_dir=tool.returnCorrectDownloadFolder(objControl.download_dir)
#Erase every file in download folder at the beginning to avoid mixed files
tool.checkDirAndCreate(download_dir)
for file in os.listdir(download_dir):
    if objControl.heroku:
        os.remove(download_dir+'/'+file)
    else:
         os.remove(download_dir+'\\'+file)

print('Download folder empty...')


browser=tool.returnChromeSettings()
idControl=objControl.idControl
querySt="select query,page,lscontrol from thesis.cjf_control where id_control="+str(idControl)+"  ALLOW FILTERING"
resultSet=bd.returnQueryResult(querySt)
lsControl=[]
StartID=0

if resultSet: 
    for row in resultSet:
        print('Service name:',str(row[0]))
        print('Starting page::',str(row[1]))
        StartID=int(str(row[1]))
        for e in row[2]:
            lsControl.append(e)
            
EndID=14000
while(StartID<=EndID):
    #This iteration gets each file
    urlExp="https://vidoc.impi.gob.mx/visor?usr=SIGA&texp=SI&tdoc=E&id="+str(lsControl[0])+"/"+str(lsControl[1])+"/"+str(lsControl[2])+"/"+str(StartID).zfill(6)
    response= requests.get(urlExp)
    status= response.status_code
    if status==200:
        print('Reading page...')
        browser.get(urlExp)
        time.sleep(10)
        if browser.find_elements_by_xpath('//*[@id="divAlertas"]/div/strong').count==0:
            print('------No existe el expediente solicitado------')
            StartID=StartID+1
            bd.updatePage(StartID)    
        else:
            print('No alert of NO FILE found...all good')
            table=browser.find_elements_by_xpath('//*[@id="MainContent_gdDoctosExpediente"]')
            #Check if the url (File= expedient) has a table, if table is  none, then skip til next url
            if table is not None:
                #Get nomber of rows of the table
                folderName=''
                folderName=browser.find_elements_by_xpath('//*[@id="MainContent_upVisor"]/h3')[0].text
                folderChunks=folderName.split(' ')
                folderName=str(folderChunks[1])
                print('Adding folder: ',folderName)
                rows = browser.find_elements_by_xpath("//*[@id='MainContent_gdDoctosExpediente']/tbody/tr")
                nRows=len(rows)+1
                for trow in range(1,nRows):
                    tool.processRows(browser,trow,folderName)
                print('-------------Page done-------------')
                StartID=StartID+1
                bd.updatePage(StartID)
            else:
                print('No table found...')

    else:
        print('The IMPI site is not responding....') 
if(StartID>=EndID):
    print('-----------------------------------------------')
    print('Please change URL, the folders are all read...') 
    print('-----------------------------------------------')                