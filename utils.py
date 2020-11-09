from selenium.webdriver.common.by import By
import cassandraSent as bd
import PyPDF2
import uuid
import base64
import time
import json
import os
import sys


download_dir='C:\\Users\\1098350515\\Downloads'

def appendInfoToFile(path,filename,strcontent):
    txtFile=open(path+filename,'a+')
    txtFile.write(strcontent)
    txtFile.close()


def processRows(browser,row):
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
                            time.sleep(20) 
                            #Get the expedient web page again, due to change of pages
                            #it is needed to come back to a prior page
                            browser.execute_script('window.history.go(-1)')
                            browser.refresh()
                            continue   
    
    #Build the json by row           
    with open('json_file.json') as json_file:
        json_doc = json.load(json_file)

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
    json_doc['pdf']=''

    strContent=''              
    for file in os.listdir(download_dir):
        pdfDownloaded=True
        strFile=file.split('.')[1]
        if strFile=='PDF' or strFile=='pdf':
            strContent=readPDF(file)        

    #When pdf is done and the record is in cassandra, delete all files in download folder
    #If the pdf is not downloaded but the window is open, save the data without pdf
    if pdfDownloaded==True:
        json_doc['pdf']=strContent
        for file in os.listdir(download_dir):
            os.remove(download_dir+'\\'+file) 

    #Insert information to cassandra
    res=bd.cassandraBDProcess(json_doc)
    if res:
        print('Record added:',str(document))
    else:
        print('Keep going...record existed:',str(document)) 
                    
"""
readPDF is done to read a PDF no matter the content, can be image or UTF-8 text
"""
def readPDF(file):
    strContent=''
    with open(download_dir+'\\'+file, "rb") as imageFile:
        bContent = base64.b64encode(imageFile.read()).decode('utf-8')
    
    strContent=bContent
    return strContent  
    
                  

def readPyPDF(file):
    #This procedure produces a b'blabla' string, it has UTF-8
    #PDF files are stored as bytes. Therefore to read or write a PDF file you need to use rb or wb.
    lsContent=[]
    pdfFileObj = open(download_dir+'\\'+file, 'rb')
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

"""
This is the method to call when fetching the pdf enconded from cassandra which is a list of text
but that text is really bytes. This will decode any file, whether image or not.bbbb
"""
def decodeFromBase64toNormalTxt(b64content):
    normarlText=base64.b64decode(b64content).decode('utf-8')
    return normarlText

"""
readPdf

This method converts from PDF to txt file
It includes the source of pdf with complete path, the destination folder and the extension
of file to convert to.
"""
def convertPdf(fileWithPath,destinationFolder,extensionToConvert): 
    #PDF pages are 0-based
    if fileWithPath.endswith(".pdf") or fileWithPath.endswith(".PDF"):
        #Split thr paths
        source_chunk=os.path.split(fileWithPath)
        sourcePath=source_chunk[0]
        sourceFile=source_chunk[1]
        
        if destinationFolder==sourcePath or destinationFolder=='':
            destinationFolder=sourcePath          
            
        pdfFileObj = open(fileWithPath, 'rb') 
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        if pdfReader.isEncrypted:
            pdfReader.decrypt('')
            
        #Get total number of pages
        nPages=pdfReader.numPages   
        i=0
        while i < nPages:
            pageObj = pdfReader.getPage(i) 
            pageContent=pageObj.extractText()
                 
            #Get the filename without extension
            destinationFileName=os.path.splitext(sourceFile)[0]
            #Create a File .txt
            pathAndFile=destinationFolder+'\\'+destinationFileName+"."+extensionToConvert
            appendInfoToFile('',pathAndFile,pageContent)
            i=i+1
            
        pdfFileObj.close() 
        return True
        
            


    
                               
                                         