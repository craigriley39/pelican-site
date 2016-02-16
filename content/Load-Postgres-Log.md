Title: Draft - Loading syslog logfile into Postgress
Date: 2016-02-15 10:20
Modified: 2016-02-15 14:20
Category: Unix
Tags: python, postgresql
Authors: Craig Riley
Summary:  Parse Syslog and loading parsed data into a Postgres SQL database


# Parsing log file and loading split data into a Postgress SQL database


This script also uses md5 to compare strings in the database with the strings in the file being parsed to ensure we arent loading duplicates. 

Script basically does:

1. Opens messages file for reading (this is mmeant ot go against a syslog server
2. Splits lines into segments
3. Performs an md5 hash of the line being loaded.
4. The Database being loaded sets the hash as a primary key. This way you can quickly attempt an insert and if the hash already exists it will fail and continue.
5. uploads the unique line to the database. 

The database structure:
```bash
logfiles=# select * from syslogs where false;
 entry_date | entry_time | source_addr | message | hash 
```
------------+------------+-------------+---------+------
(0 rows)



```python

#!/usr/bin/python

import psycopg2
import sys
import string
import re
import md5
from sh import tail
def help():
	print "Help to be written later....."
	sys.exit(0)



def pumpData(date,time,source,message,lineHash):
	""" This function can assume that we are just plowing thru data...

	"""
	con = None
	try:
		con = psycopg2.connect(database='logfiles', user='root')
		cur = con.cursor()
		query = "insert into syslogs (entry_date,entry_time,source_addr,message,hash) values (%s,%s,%s,%s,%s)"
		data = (date,time,source,message,lineHash)
		print data
		cur.execute(query,data)
		con.commit()

	except psycopg2.DatabaseError, e:
		print 'Error %s' %e
		
	finally:

		if con:
			con.close()


def tailFile(logfile):

	for line in tail("-f",logfile,_iter=True):
		parseLine(line)



def readFile(logfile):
        with open(logfile,'r') as logfile:
                loglines = logfile.readlines()
                for l in loglines:
                        parseLine(l)


def parseLine(line):
	
	lineHash = md5.md5(line).hexdigest()
        words = re.split('\s+',line)
        d = (words[0],words[1])
        date = string.join(d)+' 2013'
        time = words[2]
        source = words[3]
        msg = words[4:]
        message = string.join(msg)

	pumpData(date,time,source,message,lineHash)



if __name__ == "__main__":

	logfile = sys.argv[1]
	mode = sys.argv[2]
	if(mode == "tail"):
		tailFile(logfile)
	elif(mode == "read"):
		readFile(logfile)
	else:
		print "What mode do you want to use this in.....?"
		help()



```
