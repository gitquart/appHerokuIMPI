import json
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import os

timeOut=100
cloud_config= {
        'secure_connect_bundle': '/app/appimpi/secure-connect-dbquart.zip'
    }
              
def cassandraBDProcess(json_doc):
     
    record_added=False

    #Connect to Cassandra
    objCC=CassandraConnection()
    auth_provider = PlainTextAuthProvider(objCC.cc_user,objCC.cc_pwd)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.default_timeout=timeOut
    row=''
    value=json_doc['document']
    #Check wheter or not the record exists, check by numberFile and date
    #Date in cassandra 2020-09-10T00:00:00.000+0000
    querySt="select id from thesis.impi_docs where document='"+str(value)+"'  ALLOW FILTERING"
                
    future = session.execute_async(querySt)
    row=future.result()
    lsRes=[]
        
    if row: 
        record_added=False
        valid=''
        for val in row:
            valid=str(val[0])
        lsRes.append(record_added) 
        lsRes.append(valid)   
        cluster.shutdown()
    else:        
        #Insert Data as JSON
        jsonS=json.dumps(json_doc)           
        insertSt="INSERT INTO thesis.impi_docs JSON '"+jsonS+"';" 
        future = session.execute_async(insertSt)
        future.result()  
        record_added=True
        lsRes.append(record_added)
        cluster.shutdown()         
                    
                         
    return lsRes

def updatePage(page):

    #Connect to Cassandra
    objCC=CassandraConnection()
    auth_provider = PlainTextAuthProvider(objCC.cc_user,objCC.cc_pwd)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.default_timeout=timeOut
    page=str(page)
    querySt="update thesis.cjf_control set page="+page+" where id_control=3;"          
    future = session.execute_async(querySt)
    future.result()
                         
    return True

def getPageAndTopic():

    #Connect to Cassandra
    objCC=CassandraConnection()
    auth_provider = PlainTextAuthProvider(objCC.cc_user,objCC.cc_pwd)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.default_timeout=timeOut
    row=''
    querySt="select query,page from thesis.cjf_control where id_control=3  ALLOW FILTERING"           
    future = session.execute_async(querySt)
    row=future.result()
    lsInfo=[]
        
    if row: 
        for val in row:
            lsInfo.append(str(val[0]))
            lsInfo.append(str(val[1]))
            print('Value from cassandra:',str(val[0]))
            print('Value from cassandra:',str(val[1]))
        cluster.shutdown()
                    
                         
    return lsInfo    


def insertPDF(json_doc):
     
    record_added=False

    #Connect to Cassandra
    objCC=CassandraConnection()
    auth_provider = PlainTextAuthProvider(objCC.cc_user,objCC.cc_pwd)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.default_timeout=timeOut

    iddocumento=str(json_doc['idDocumento'])
    documento=str(json_doc['documento'])
    fuente=str(json_doc['fuente'])
    secuencia=str(json_doc['secuencia'])
    querySt="select id from thesis.tbDocumento_impi where iddocumento="+iddocumento+" and documento='"+documento+"' and fuente='"+fuente+"' AND secuencia="+secuencia+"  ALLOW FILTERING"          
    future = session.execute_async(querySt)
    row=future.result()

    if row:
        cluster.shutdown()
    else:    
        jsonS=json.dumps(json_doc)           
        insertSt="INSERT INTO thesis.tbDocumento_impi JSON '"+jsonS+"';" 
        future = session.execute_async(insertSt)
        future.result()  
        record_added=True
        cluster.shutdown()     
                    
                         
    return record_added         

   
class CassandraConnection():
    cc_user='quartadmin'
    cc_keyspace='thesis'
    cc_pwd='P@ssw0rd33'
        

