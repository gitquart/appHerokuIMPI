from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import cassandraSent as bd
import PyPDF2
import uuid
import base64
import time
import json
import os
import sys
from textwrap import wrap
from selenium import webdriver
from InternalControl import cInternalControl
from selenium.webdriver.chrome.options import Options

objControl=cInternalControl()



def checkDirAndCreate(folder):
    print('Checking if download folder exists...')
    folder=returnCorrectDownloadFolder(folder)
    isdir = os.path.isdir(folder)
    if isdir==False:
        print('Creating download folder...')
        os.mkdir(folder)  

def returnCorrectDownloadFolder(folder):
    if objControl.heroku:
        folder='/app/'+objControl.download_dir
    else:
        folder='C:\\'+objControl.download_dir

    return folder 

def returnChromeSettings():
    browser=''
    chromedriver_autoinstaller.install()
    if objControl.heroku:
        #Chrome configuration for heroku
        chrome_options= webdriver.ChromeOptions()
        chrome_options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")

        browser=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=chrome_options)

    else:
        options = Options()
        profile = {"plugins.plugins_list": [{"enabled": True, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": objControl.download_dir , 
               "download.prompt_for_download": False,
               "download.directory_upgrade": True,
               "download.extensions_to_open": "applications/pdf",
               "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
               }           

        options.add_experimental_option("prefs", profile)
        browser=webdriver.Chrome(options=options)  

    

    return browser 


def appendInfoToFile(path,filename,strcontent):
    txtFile=open(path+filename,'a+')
    txtFile.write(strcontent)
    txtFile.close()


def processRows(browser,row,folderName):
    pdfDownloaded=False
    for col in range(2,8):
        xPathContent='//*[@id="MainContent_gdDoctosExpediente"]/tbody/tr['+str(row)+']/td['+str(col)+']';
        if col==2:
            barcode=browser.find_elements_by_xpath(xPathContent)[0].text
            continue
        if col==3:
            document=browser.find_elements_by_xpath(xPathContent)[0].text
            continue
        if col==4:
            description=browser.find_elements_by_xpath(xPathContent)[0].text
            continue
        if col==5:
            typeDoc=browser.find_elements_by_xpath(xPathContent)[0].text
            continue
        if col==6:
            dt=browser.find_elements_by_xpath(xPathContent)[0].text  
            continue  
        if col==7:
            if objControl.enablePdf:
                row=int(row)-1
                javaScript = "document.getElementById('MainContent_gdDoctosExpediente_ImageButton1_"+str(row)+"').click();"
                browser.execute_script(javaScript)
                #Get the name of the pdf document
                time.sleep(10)
                pdf_name=document.replace('/','_')
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
                    linkFound=False
                    for link in lst_link:
                        if linkFound==False:   
                            if link.text=='aquí':
                                linkFound=True
                                link.click()
                                #Wait 'X' seconds for download
                                time.sleep(40) 
                                #Get the expedient web page again, due to change of pages
                                #it is needed to come back to a prior page
                                browser.execute_script('window.history.go(-1)')
                                browser.refresh()
                                continue   
    
    #Build the json by row   
    if objControl.heroku:        
        json_doc=devuelveJSON('/app/'+objControl.hfolder+'/json_file.json')
    else:
        json_doc=devuelveJSON(objControl.rutaLocal+'/json_file.json')
            
    json_doc['folder']=folderName
    json_doc['id']=str(uuid.uuid4())
    json_doc['barcode']=barcode
    json_doc['document']=document
    #Working with the date, this field will deliver:
    #1.Date field,2. StrField and 3.year
    # timestamp accepted for cassandra: 
    # yyyy-mm-dd  , yyyy-mm-dd HH:mm:ss
    #In web site, the date comes as 27-10-2020 14:38:00
    data=''
    data=dt.split(' ')
    dDate=str(data[0]).split('-')
    dDay=dDate[0]
    dMonth=dDate[1]
    dYear=dDate[2]
    fullTimeStamp=dYear+'-'+dMonth+'-'+dDay;
    json_doc['description']=description
    json_doc['typedoc']=typeDoc
    json_doc['dt']=fullTimeStamp
    json_doc['strdt']=fullTimeStamp
    json_doc['year']=int(dYear)
    #Check if a pdf exists 

    if not objControl.enablePdf:
        print('Adding a time sleep of 10 secs to slow down cassandra...(when pdf is off only)')
        time.sleep(10)

    #Insert information to cassandra
    lsRes=bd.cassandraBDProcess(json_doc)
    if lsRes[0]:
        print('Record added:',str(document))
    else:
        print('Keep going...record existed:',str(document))
                            

   
    if objControl.enablePdf: 
        download_dir=returnCorrectDownloadFolder(objControl.download_dir)    
        for file in os.listdir(download_dir):
            pdfDownloaded=True
            processPDF(json_doc,lsRes)
            if objControl.heroku:
                os.remove(download_dir+'/'+file)
            else:    
                os.remove(download_dir+'\\'+file)
        
            


"""
readPDF is done to read a PDF no matter the content, can be image or UTF-8 text
"""
def readPDF(file):  
    with open(download_dir+'/'+file, "rb") as pdf_file:
        bContent = base64.b64encode(pdf_file.read()).decode('utf-8')
    
    return bContent  
    

"""
This is the method to call when fetching the pdf enconded from cassandra which is a list of text
but that text is really bytes.
"""
def decodeFromBase64toNormalTxt(b64content):
    normarlText=base64.b64decode(b64content).decode('utf-8')
    return normarlText


def getPDFfromBase64(bContent):
    #Tutorial : https://base64.guru/developers/python/examples/decode-pdf
    bytes = base64.b64decode(bContent, validate=True)
    # Write the PDF contents to a local file
    f = open(download_dir+'/result.pdf', 'wb')
    f.write(bytes)
    f.close()
    return "PDF delivered!"

def TextOrImageFromBase64(bContent):
    #If sData got "EOF" is an image, otherwise is TEXT
    sData=str(bContent)
    if "EOF" in sData:
        res=getPDFfromBase64(bContent) 
    else:
        res=decodeFromBase64toNormalTxt(bContent)

    return res 

def devuelveJSON(jsonFile):
    with open(jsonFile) as json_file:
        jsonObj = json.load(json_file)
    
    return jsonObj 

def processPDF(json_sentencia,lsRes):
    lsContent=[]  
    for file in os.listdir(download_dir): 
        strFile=file.split('.')[1]
        if strFile=='PDF' or strFile=='pdf':
            strContent=readPDF(file) 
            print('Start wrapping text...') 
            lsContent=wrap(strContent,1000) 
            if objControl.heroku: 
                json_documento=devuelveJSON('/app/'+objControl.hfolder+'/json_documento.json')
            else:
                json_documento=devuelveJSON(objControl.rutaLocal+'/json_documento.json')

            if lsRes[0]:
                json_documento['idDocumento']=json_sentencia['id']
            else:
                json_documento['idDocumento']=lsRes[1]

            json_documento['documento']=json_sentencia['document']
            json_documento['fuente']='impi'
            totalElements=len(lsContent)
            result=insertPDFChunks(0,0,0,totalElements,lsContent,json_documento,0)
            if result==False:
                print('PDF Ended!')       
           
        
def insertPDFChunks(startPos,contador,secuencia,totalElements,lsContent,json_documento,done):
    if done==0:
        json_documento['lspdfcontent'].clear()
        json_documento['id']=str(uuid.uuid4())
        for i in range(startPos,totalElements):
            if i!=totalElements-1:
                if contador<=20:
                    json_documento['lspdfcontent'].append(lsContent[i])
                    contador=contador+1
                else:
                    currentSeq=secuencia+1
                    json_documento['secuencia']=currentSeq
                    res=bd.insertPDF(json_documento) 
                    if res:
                        print('Chunk of pdf added:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq))  
                    else:
                        print('Chunk of pdf already existed:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq)) 

                    return insertPDFChunks(i,0,currentSeq,totalElements,lsContent,json_documento,0) 
            else:
                json_documento['lspdfcontent'].append(lsContent[i])
                currentSeq=secuencia+1
                json_documento['secuencia']=currentSeq
                res=bd.insertPDF(json_documento) 
                if res:
                    print('Last Chunk of pdf added:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq))
                else:
                    print('Last Chunk of pdf already existed:',str(i),'from ',str(totalElements),' sequence:',str(currentSeq))

                return  insertPDFChunks(i,0,currentSeq,totalElements,lsContent,json_documento,1)
    else:
        return False            

                             
def readPyPDF(file):
    #This procedure produces a b'blabla' string, it has UTF-8
    #PDF files are stored as bytes. Therefore to read or write a PDF file you need to use rb or wb.
    lsContent=[]
    pdfFileObj = open(download_dir+'/'+file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pags=pdfReader.numPages
    for x in range(0,pags):
        pageObj = pdfReader.getPage(x)
        #UTF-8 is the right encodeing, I tried ascii and didn't work
        #1. bContent is the actual byte from pdf with utf-8, expected b'bla...'
        bcontent=base64.b64encode(pageObj.extractText().encode('utf-8'))
        lsContent.append(str(bcontent.decode('utf-8')))
                         
    pdfFileObj.close()    
    return lsContent                      