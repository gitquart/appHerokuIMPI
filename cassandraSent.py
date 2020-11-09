import json
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import os

pathToHere=os.getcwd()

cloud_config= {
        'secure_connect_bundle': pathToHere+'\\secure-connect-dbquart.zip'
    }
              
def cassandraBDProcess(json_doc):
     
    record_added=False

    #Connect to Cassandra
    objCC=CassandraConnection()
    auth_provider = PlainTextAuthProvider(objCC.cc_user,objCC.cc_pwd)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.default_timeout=70
    row=''
    value=json_doc['document']
    #Check wheter or not the record exists, check by numberFile and date
    #Date in cassandra 2020-09-10T00:00:00.000+0000
    querySt="select id from thesis.impi_docs where document='"+str(value)+"'  ALLOW FILTERING"
                
    future = session.execute_async(querySt)
    row=future.result()
        
    if row: 
        record_added=False
        cluster.shutdown()
    else:        
        #Insert Data as JSON
        jsonS=json.dumps(json_doc)           
        insertSt="INSERT INTO thesis.impi_docs JSON '"+jsonS+"';" 
        future = session.execute_async(insertSt)
        future.result()  
        record_added=True
        cluster.shutdown()     
                    
                         
    return record_added

def updatePage(page):

    #Connect to Cassandra
    objCC=CassandraConnection()
    auth_provider = PlainTextAuthProvider(objCC.cc_user,objCC.cc_pwd)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.default_timeout=70
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
    session.default_timeout=70
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

   
class CassandraConnection():
    cc_user='quartadmin'
    cc_keyspace='thesis'
    cc_pwd='P@ssw0rd33'
        

