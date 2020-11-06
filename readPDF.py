#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 16:41:05 2020
@author: ulysesrico
-This program converts from PDF to txt file
"""


# importing required modules 
import PyPDF2 
import os
import writeFile as wf

"""
readPdf

It includes the source of pdf with complete path, the destination folder and the extension
of file to convert to.
"""
def readPdf(fileWithPath,destinationFolder,extensionToConvert):
     
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
            wf.appendInfoToFile(pathAndFile,pageContent)
            i=i+1
            
        pdfFileObj.close() 
        return True
        
        
        
      
        
