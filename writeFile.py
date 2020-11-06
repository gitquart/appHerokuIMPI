#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 09:34:08 2020

@author: quart

Program: Create a file with any extension
"""

def appendInfoToFile(fileandpath,strcontent):
    txtFile=open(fileandpath,'a+')
    txtFile.write(strcontent)
    txtFile.close()
