Title: Draft - Gather System Data and load into a database
Date: 2016-02-15 10:20
Modified: 2016-02-15 14:20
Category: Unix
Tags: python, postgres
Authors: Craig Riley
Summary:  Script to gather basic system data and load into a post gres datbase

#Gather system data and load into a database
This is a scirpt that I cant remember if it works at all to be honest :) 

I'm sure that parts of it work so that's cool. 

This script will run some basic stat gathering items on the server and load it into a database. Honestly it wasn't very useful but I ran this on my syslog server that was serioulsy getting pounded. The effort was abandoned as there were many ways to get what you need without all the effort. 

```python
#!/usr/bin/env python

import psutil
import datetime
import mysql.connector

def loadDB(boot,vm,cpu,du,eth0):
	dbuser = "load"
	dbpass = "daemon12"
	dbname = "sysinfo"
	entry_date = datetime.datetime.now()	
	cnx = mysql.connector.connect(user='load',password='daemon12',host='localhost',database='sysinfo')
	
	cursor = cnx.cursor()
	query = ("insert into sys "
	"(entry_date,uptime,mem_usage,cpu_usage,disk_usage,net_packets_in_drop,net_packets_out_drop)"
	"VALUES (%s,%s, %s, %s, %s, %s, %s)")
	
	data_stats = (entry_date,boot,vm,cpu,du,eth0.dropin,eth0.dropout)
	
	cursor.execute(query,data_stats)
	cnx.commit()
	entry_number = cursor.lastrowid
	cursor.close()
	cnx.close()

def network_io():
	nt = psutil.net_io_counters(pernic=True)
	eth0 = nt['eth0']
	return eth0
	
def bootTime():
	
	bt = psutil.boot_time()
	bTime = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
	return bTime

def virtMemory():
	mem = psutil.virtual_memory()
	mp = mem.percent
	return mp

def cpuPercent():
	cpuPercent = psutil.cpu_percent(interval=None,percpu=False)
	return cpuPercent

def diskUsage():
	
	freeSpace = psutil.disk_usage('/')
	fs = freeSpace.percent
	return fs

def main():
	boot = bootTime()
	vm =   virtMemory()
	cpu = cpuPercent()	
	du = diskUsage()	
	eth0 = network_io()	
	loadDB(boot,vm,cpu,du,eth0)

if __name__ == "__main__":
   main()


```
