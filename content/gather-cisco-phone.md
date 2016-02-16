Title: Draft - Gather Cisco Phone Stats
Date: 2016-02-15 10:20
Modified: 2016-02-15 10:20
Category: Unix
Tags: python
Authors: Craig Riley
Summary: Draft - Gather Cisco phone stats

#Gather data from connecting directly to phones on a subnet and query stats

We were looking for data on a jitter rates, connection time, firware versions etc. 

This script will query every phone connected to a spefici switch and plug those elemintes into a database for query later.



This script was orig. created by Mike Orstead (Unix Guru) and lent to me. I then tweaked it to work in our environment, grab a few extra details from the phones and plug everything into a database.  - Thanks Mike!


```python
#!/usr/bin/python
import os
import re
import pexpect
import getpass
import urllib2
import socket
import datetime
import psycopg2




def parseDeviceInfo(phoneDetail,hostName):
    outfile = open('/tmp/phoneDiscovery.csv','a')
    # set the socket timeout to 10 seconds so that we dont wait forever if a phone doesnt respond
    socket.setdefaulttimeout(10)
    print "Calling function parsePhoneNetworkInfo"
    # here we should define all the global variables we will want to use for the rest of this function
   
    # we need to establish the date and time for our database update.
    now = datetime.datetime.now()
    curDate = now.strftime("%Y-%m-%d")
    curTime = now.strftime("%H:%M:%S") 
    avgJitter = ''
    avgMos = ''
    minMos = ''
    maxMos = ''
    latency = ''
    port1Cfg = ''
    port2Cfg = ''
    macAddr = ''
    phoneDN = ''
    
    # now lets roll through each phone listing and gaathe our stuff. 
    for key in phoneDetail.iterkeys():
        
        # url for the device network stats
        url = 'http://'+phoneDetail[key]+'/StreamingStatistics?1'
        print "Trying to open URL:",url
        
        try:
            urlOutPut = urllib2.urlopen(url)
            # now lets try to get the pieces we need out of the info
            outputParts = re.split('<TR>',urlOutPut.read())
        except IOError as err:
            print "Error",str(err)
            continue
        
        for line in outputParts:
            # this is where we would search for stuff.
            if re.search('Avg MOS LQK',line):
                #print line
                parts = re.split('</TD>',line)
                avgMos = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()
            
            if re.search('Min MOS LQK',line):
                parts = re.split('</TD>',line)
                minMos = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()
            
            if re.search('Max MOS LQK',line):
                parts = re.split('</TD>',line)
                maxMos = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()
                
            if re.search('Avg Jitter',line):
                parts = re.split('</TD>',line)
                avgJitter = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()
                
            if re.search('Latency',line):
                parts = re.split('</TD>',line)
                latency = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()
            
            try:
                avgJitter = avgJitter
               
            except:
                avgJitter = 'unknown'
            
            try:
                minMos = minMos
            
            except:
                minMos = 'unknown'
                
            try:
                avgMos = avgMos
            
            except:
                avgMos = 'unknown'
            try:
                maxMos = maxMos
            except:
                maxMos = 'unknown'
                
            try:
                latency = latency
            except:
                latency = 'unknown'
                
            
        
        # url for the device network stats
        url = 'http://'+phoneDetail[key]+'/PortInformation?1'
        print "Trying to open URL:",url
        
        try:
            urlOutPut = urllib2.urlopen(url)
            # now lets try to get the pieces we need out of the info
            outputParts = re.split('<TR>',urlOutPut.read())
        except IOError as err:
            print "Error",str(err)
        
        
        for line in outputParts:
            # this is where we would search for stuff.
            if re.search('Port 1',line):
                #print line
                parts = re.split('</TD>',line)
                port1Cfg = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()
                port1Cfg = re.sub(',','-',port1Cfg)
            
            if re.search('Port 2',line):
                parts = re.split('</TD>',line)
                port2Cfg = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()
                port2Cfg = re.sub(',','-',port2Cfg)
        
        try:
            port1Cfg = port1Cfg
        except:
            port1cfg = 'unknown'
        try:
            port2Cfg = port2Cfg
        except:
            port2Cfg = 'unknown'
        
           
    
    
        # now lets roll through each phone listing and gaathe our stuff. 
    
        
        # url for the device network stats
        url = 'http://'+phoneDetail[key]
        print "Trying to open URL:",url
        
        try:
            urlOutPut = urllib2.urlopen(url)
            # now lets try to get the pieces we need out of the info
            outputParts = re.split('<TR>',urlOutPut.read())
        except IOError as err:
            print "Error",str(err)
            
        
        for line in outputParts:
            # this is where we would search for stuff.
            if re.search('MAC Address',line):
                #print line
                try:
                    parts = re.split('</TD>',line)
                    macAddr = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()
                except:
                    macAddr = 'unknown'
            if re.search('Phone DN 1',line):
                parts = re.split('</TD>',line)
                phoneDN = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()
        
        try:
            macAddr = macAddr
        except:
            macAddr = 'unknown'
        try:
            phoneDN = phoneDN
        except:
            phoneDN = 'unknown'
    
        """    
        avgJitter = ''
        avgMos = ''
        minMos = ''
        maxMos = ''
        latency = ''
        port1Cfg = ''
        port2Cfg = ''
        macAddr = ''
        phoneDN = ''
        """
        #/StreamingStatistics?2

	 # url for the device network stats
        url = 'http://'+phoneDetail[key]+'/StreamingStatistics?2'
        print "Trying to open URL:",url

        try:
            urlOutPut = urllib2.urlopen(url)
            # now lets try to get the pieces we need out of the info
            outputParts = re.split('<TR>',urlOutPut.read())
        except IOError as err:
            print "Error",str(err)


        for line in outputParts:
            # this is where we would search for stuff.
            if re.search('Remote Address',line):
                #print line
                parts = re.split('</TD>',line)
                remoteAddr = re.sub('<TD><B>|</B>','',parts[2]).rstrip().lstrip()

        try:
            remoteAddr = remoteAddr
        except:
            remoteAddr = 'unknown'

        con = None
        try:
                con = psycopg2.connect(database='phones', user='root')
                cur = con.cursor()
                query = "insert into info (entry_date,entry_time,switch_ip,dev_name,phone_ip,mac_addr,ext,minMos,maxMos,avgMos,latency,avgJitter,port1Cfg,port2Cfg,remoteAddr) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                data = (curDate,curTime,hostName,key,phoneDetail[key],macAddr,phoneDN,minMos,maxMos,avgMos,latency,avgJitter,port1Cfg,port2Cfg,remoteAddr)

                print query
                print data
                cur.execute(query,data)
                con.commit()

        except psycopg2.DatabaseError, e:
                print 'Error %s' %e

        finally:

                if con:
                        con.close()
 
        print hostName+','+key+','+phoneDetail[key]+','+macAddr+','+phoneDN+','+minMos+','+maxMos+','+avgMos+','+latency+','+avgJitter+','+port1Cfg+','+port2Cfg+'\n'
        
        #outfile.write(hostName+','+key+','+phoneDetail[key]+','+macAddr+','+phoneDN+','+minMos+','+maxMos+','+avgMos+','+latency+','+avgJitter+','+port1Cfg+','+port2Cfg+'\n')
        
                
     
    
    #outfile.close()
       
    
    
    
    
    
def remoteConnect(hostName,userName,userPass):
    phones = {}
    phoneDetail = {}
    tmpf = os.tmpfile()
    con = pexpect.spawn('ssh '+userName+'@'+hostName)
    con.expect('word:')
    con.sendline(userPass)
    con.expect('\d#')
    con.sendline('term len 0')
    con.expect('#')
    # Gather device name / port
    con.logfile = tmpf
    con.sendline('show cdp neighbor | include SEP')
    con.expect('#')
    con.logfile = None
    
    tmpf.seek(0)
    outputBuffer = tmpf.readlines()
    phoneCount = 0
    phoneList = []
    for line in outputBuffer:
        if re.search('SEP',line):
            phoneList.append(line)
   
    print "Current count of phones:",len(phoneList)
    currentNumberofPhones = len(phoneList)
    with open('/tmp/phoneDiscovery.csv','a') as outfile:
        outfile.write('Hostname: '+hostName+'\n')
        outfile.write('Current count of connected phones: '+str(currentNumberofPhones)+'\n\n')
        outfile.write('Switch Name,PhoneName,Phone IP,Mac Address,Extention,Min Mos,Max Mos,Avg MOS,Latency,Avg Jitter,Phone Port 1 Duplex,Phone Port 2 Duplex\n')
    for l in phoneList:
        # i need to take each entry and get the phone's device name and its port.
        plist = re.split('\s',l)
        phones[plist[0]] = plist[2]+' '+plist[3]
    
    for key in phones.iterkeys():
        print key,phones[key]
        dtmpf = os.tmpfile()
        con.logfile = dtmpf
        
        print "We will be looking for this:",phones[key]
        con.sendline('show cdp neighbor '+phones[key]+' detail')
        con.expect('\d#')
        con.logfile=None
        dtmpf.seek(0)
        outputBuffer = dtmpf.readlines()
        # loop through the outputBuffer and grab the IP
        # here is the tough part...i need to have a hash that holds a few things. phoneDetail[key][ip] & phoneDetail[key][deplex]
        # might be easier just to focus on item 3
        for line in outputBuffer:
            if re.search('IP address',line):
                ip = re.sub('IP address: ','',line)
                ip = ip.rstrip()
                ip = ip.lstrip()
                phoneDetail[key] = ip
            else:
                print "Here is the line:",line
        for nkey in phoneDetail.iterkeys():
            print nkey,phoneDetail[nkey]
            
    print "disconnecting from device",hostName    
    con.sendline('exit')
    
    parseDeviceInfo(phoneDetail,hostName)
def main():
    """
    This function willbe used to gather some information and call the rest
    ### Change Log:
     
    Todo: Need to grab a few more pieces of info from the page.
    1. Capture the port in the output ( we already grab this prior to show cdp neighbor ... detail)
    2. Capture the duplex setting on the output of the above command.
    3. on the page: http://10.239.174.43/PortInformation?1 of the phone...we would have to start the query for the same device again.
        - we need to grab Port 1 and Port 2 (network settings)
        - so right now we jump from main -> remoteConnect() and then loop through devices -> parseDeviceInfo().
        I think i'll add another def like parseDeviceInfo called parsePhoneNetworkInfo() and call that with the same loop.
        
        
        
    Thats it for now.
    """
    #hostName = raw_input('What host are we connecting to: ').lower()
    #userName = raw_input('Username: ')
    #userPass = getpass.getpass('Password: ')
    userName='#########'
    userPass='#########'
    
    
    
    
    #outFile = '/tmp/phoneDiscovery'+hostName+".csv"
    hostName = ''
    print "connecting to remote host"
    sites = ['192.168.0.1'] # you are gonna need to provide a list of switches to connect to.
    for hostName in sites:
        remoteConnect(hostName,userName,userPass)
if __name__ == "__main__":
   main()




```
