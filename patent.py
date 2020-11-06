"""
Quart: This program is a 'Demo' that will read patents and store them in a spreadsheet

"""

from selenium import webdriver
import chromedriver_autoinstaller
import time
import requests 
from selenium.webdriver.chrome.options import Options
import os



chromedriver_autoinstaller.install()
download_dir='C:\\Users\\1098350515\\Downloads'
#Set options for chrome
options = Options()
profile = {
           "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
           "download.default_directory": download_dir , 
           "download.extensions_to_open": "applications/pdf",
           "plugins.always_open_pdf_externally": True
           }

options.add_experimental_option("prefs", profile)

browser=webdriver.Chrome(options=options)
#Start 13000
StartID=5000
EndID=14000
countExpedient=0


for i in range(StartID,EndID):
    #This iteration gets each file
    urlExp="https://vidoc.impi.gob.mx/visor?usr=SIGA&texp=SI&tdoc=E&id=MX/a/2015/00"+str(i)
    response= requests.get(urlExp)
    status= response.status_code
    if status==200:
        browser.get(urlExp)
        time.sleep(1)
        path=''
        pathPdf=''
        expedient_name=''
        exp_html=''
        table=''
        exp_html = BeautifulSoup(browser.page_source, 'lxml')
        time.sleep(3)
        table=exp_html.find('table')
        expedient_name=exp_html.find('h3').text
        expedient_name=expedient_name.replace(' ','_')  
        expedient_name=expedient_name.replace('/','_') 
        path=download_dir+expedient_name+'.xlsx'
        res=os.path.isfile(path)
        if res==False:
            if table is not None:
                #The complete table if exists
                table_rows = table.findAll('tr')
                #Iterate all the rows in the table
                countPatent=0
                for tr in table_rows:
                    #Every <td> has one element only
                    txt_number=''
                    txt_barcode=''
                    txt_document=''
                    txt_desc=''
                    txt_type=''
                    txt_date=''
                    pdf_name=''
                    pdf_file_name=''
                    if tr.nextSibling!='\n':
                        td = tr.findAll('td')
                        fieldPosition=0
                        for t in td:
                            fieldPosition=fieldPosition+1
                            #Id of the input for each row index 0
                            #MainContent_gdDoctosExpediente_ImageButton1_0 
                            btn=t.findChildren('input',recursive=True)
                            if btn:
                                chunks=str(btn[0]).split(' ')
                                #Getting ID alone
                                parts=chunks[2].split('=')
                                val_name=parts[1] 
                                javaScript = "document.getElementsByName("+val_name+")[0].click();"
                                browser.execute_script(javaScript)
                                #Get the name of the pdf document
                                time.sleep(3) #Time sleep to give time to read the 'modal-text'
                                pdf_name=txt_document.replace('/','_')
                                pdf_file_name=pdf_name+'.pdf'
                                pdf_source=''
                                pdf_source = browser.find_element_by_tag_name('iframe').get_attribute("src")
                                time.sleep(2)
                                if pdf_source!='':
                                    #Get the url of the source
                                    browser.get(pdf_source)
                                    time.sleep(5)
                                    #Finf the href with innerText 'aquí'
                                    lst_link=browser.find_elements_by_tag_name('a')
                                    for link in lst_link:   
                                        if link.text=='aquí':
                                            link.click()
                                            #Wait 'X' seconds for download
                                            time.sleep(10) 
                                            #Get the expedient web page again, due to change of pages
                                            #it is needed to come back to a prior page
                                            browser.execute_script('window.history.go(-1)')
                                            browser.refresh()
                                            continue
                                            
                                           
                            else:
                             
                        
                   
                        #if countRow==1:
                        #    break
                #End of row loop 
                countExpedient=countExpedient+1
                print('Expedients so far:',str(countExpedient))                    
                if countExpedient==47:
                    break        
        
browser.quit() 

    
       
        
   