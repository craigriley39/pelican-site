Title: Draft - Ping Check
Date: 2016-02-15 10:20
Modified: 2016-02-15 10:20
Category: Unix
Tags: bash
Authors: Craig Riley
Summary: Draft - Simple Ping check

# Scanning for available IP's


So I worked for a company that had some aversion to using DNS for its server subnets...I have no freaking idea why!

The task was to take this manually created list of IP addresses that had been assigned or reserved for some reason at some point in the past and validate that they were valid of if they werent.  

for the record - nmap will do this in a jiff
```bash
#!/bin/bash

OUTFILE=host-results
IPFILE=hosts.txt

if [ -e $OUTFILE ]
then
	rm $OUTFILE
fi


for I in `cat $IPFILE` 
do 
	echo "-------------- CHECKING $I ----------------" >> $OUTFILE
	echo "Checking $I" >> $OUTFILE 

DNS=`host $I`
if [ $? == 0 ] 
then 
	echo "$I is in DNS -> $DNS" >>$OUTFILE 
else 
	echo "$I is NOT in DNS." >> $OUTFILE
fi

PING=`ping -c 2 $I`
if [ $? == 0 ]
then 
	echo "$I is pinging -- IP in use." >> $OUTFILE 
else 
	echo "$I is NOT pinging -- IP is likely free." >> $OUTFILE 
fi 
	echo "---------------- DONE CHECKING $I ------------" >> $OUTFILE
done 
```
