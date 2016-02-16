Title: Draft - Setup SFTP User
Date: 2016-02-15 10:20
Modified: 2016-02-15 14:20
Category: Unix
Tags: python, ssh
Authors: Craig Riley
Summary:  Script to automate new user creation 

#Setup new user - generate password

The company I worked at had an externally facing SFTP server I built with a chroot jail.

I wrote this script to automate creating new user accounts as well as defining a default password ala a random generator. 

```python
#!/usr/bin/python

import os
import string
import sys
import re
import random
import datetime
from subprocess import Popen,PIPE

print """

Hello...this script will assist with configuring users on the sftp server

We will need to gather some information first.

"""
def executeShellCommand(cmd):
    stdOut = ''
    errOut = ''
    p = Popen(cmd, stderr=PIPE,stdout=PIPE,shell=True)
    return_code = p.wait()
    
    for line in p.stdout:
	stdOut += line.rstrip()+'\n'	
    for line in p.stderr:
        errOut += line.rstrip()+'\n'
    
    return return_code,stdOut,errOut


def passwordGenerator():
    pwLength = 9
    password = []
    punctuation = ['#','@','^','*']
    
    for grp in (string.ascii_letters,punctuation,string.digits):
        password += random.sample(grp,3)
        
    password += random.sample(
                 string.ascii_letters + string.punctuation + string.digits,
                 pwLength - len(password))

    random.shuffle(password)
    password = ''.join(password)
        
    return password

def createUser(userName,tempUser,accountExpiresOn,sftpOnly,userPassword):
    createUserCmd = string.join(['useradd -c "Generated User - '+userName+'"',userName])
    modifyUserDir = string.join(['usermod -d /'+userName,userName])
    createUserDir = string.join(['mkdir /chroot/'+userName,';mkdir /chroot/'+userName+'/incoming ; mkdir /chroot/'+userName+'/outgoing'])
    chownUserDir = string.join(['chown -R ',userName,'/chroot/'+userName])
    
    
        
    return_code,stdout,stderr = executeShellCommand(createUserCmd)
    
    if return_code == 0:
        print "Created user account"
    else:
        print "Failed to create user account",str(stdout),str(stderr)
        sys.exit(1)
        
    
    return_code,stdout,stderr = executeShellCommand(modifyUserDir)
    if return_code == 0:
        print "Updated userdir to use chroot"
    else:
        print "Failed to update user directory in /etc/passwd",str(stdout),str(stderr)
        sys.exit(1)
        
        
    print "Creating userdir in chroot"
    return_code,stdout,stderr = executeShellCommand(createUserDir)
    if return_code == 0:
        print "Created user directory"
    else:
        print "Failed to create user direcotry in /chroot",str(stdout),str(stderr)
        sys.exit(1)
        
    print "Modifying ownership of chroot homedir"
    return_code,stdout,stderr = executeShellCommand(chownUserDir)
    if return_code == 0:
        print "Modified ownership of chroot home directory"
    else:
        print "Failed to chown the home directory",str(stdout),str(stderr)
        sys.exit(1)
    
    
    if sftpOnly == True:
        print "Adding user to sftponly group"
        sftpGrpCmd = string.join(['usermod -G sftponly',userName])
        return_code,stdout,stderr = executeShellCommand(sftpGrpCmd)
        if return_code == 0:
            print "updated group membership for user to use sftponly"
        else:
            print "Failed to update group membership",str(stdout),str(stderr)
            sys.exit(1)
        
    if tempUser == True:
        
        print "Setting Expiration on account"
        expireAcctCmd = string.join(['usermod -e',str(accountExpiresOn),userName])
        return_code,stdout,stderr = executeShellCommand(expireAcctCmd)
        if return_code == 0:
            print "Users account has been set to expire on",str(accountExpiresOn)
        else:
            print "Failed to update expiration date on the user account",str(stdout),str(stderr)
            sys.exit(1)
            
    else:
        print "Setting account to never expire"
        
    
        
    passwordSetCommand = string.join(['echo "'+userPassword+'"| passwd --stdin',userName])
    
    return_code,stdout,stderr = executeShellCommand(passwordSetCommand)
    if return_code == 0:
        print "Checked the strength of the password with cracklib-check"
    else:
        print "Failed to set user password",str(stdout),str(stderr)
        sys.exit(1)
    
    
    print """
    --------------------------------------
    --------------------------------------
    """
    print "The account is setup."
    print "You will want to send the information below to the user"
    print "-------------------------"
    print "ServerName: sftp.graebel.com"
    print "Username: ",userName
    print "Password: ",userPassword
    print "-------------------------"
    

def setPassword():
    """
    for this to work we will need to use Popen to captre stdout and stderr to see what the actual result of cracklib-check was
    
    """
    stdout = ''
    errout = ''

    genPW = raw_input("Would you like to generate a password? [y|n]")
    if re.match('y|Y',genPW):
        userPassword = passwordGenerator()
    else:
        userPassword = raw_input("Enter password for new user:")
        ckPWStrength = string.join(['echo \"',userPassword,'"| cracklib-check'])
        
        return_code,stdout,stderr = executeShellCommand(ckPWStrength)
        if return_code == 0:
            
            if re.match('^'+userPassword+': OK',stdout):
                print "Your password seems to be complex enough",str(stdout)
            else:
                print "The password choosen does not meet the system requirements. YOU NEED TO CHOOSE ANOTHER PW or let us create one",str(stdout)
                print stdout
                setPassword()
            
    
    return userPassword
    
def setupNewUser():
    if os.geteuid() != 0:
        print "You need to run this script with root privileges"
        sys.exit(1)
    userName = raw_input("What username should we use? [string 6-8 characters]: ")
    tempUser = raw_input("Is this a Temp User? [y|n]")
    if re.match('y|Y',tempUser):
        print "User account will be set to expire."
        tempUser = True
        expireInDays = raw_input("How many days until account expires? [enter a digit]: ")
        expireInDays = int(expireInDays)
        accountExpiresOn = datetime.date.today() + datetime.timedelta(days=expireInDays)
        print "The account will expire on :"+str(accountExpiresOn)
    else:
        tempUser = False
        expireInDays = 0
        accountExpiresOn = 'NEVER'
        print "This account will NOT expire"
        
    sftpOnly = raw_input("Will this user be just sftp? [y|n]")
    if re.match('y|Y',sftpOnly):
        print "User will only be able to sftp to the server"
        sftpOnly = True
    else:
        sftpOnly = False
    
    userPassword = setPassword()
    
    print """
    Please review the information below:
    
    """
    print "Username: ",userName
    print "Temp User? ",tempUser
    print "Account Expires on: ",accountExpiresOn
    print "SFTP Only? ",sftpOnly
    print "Password: ",userPassword
    print """
    
    
    ------------------------------------
    """
    answer = raw_input("Continue? [y|n]")
    if re.match('y|Y',answer):
        
        createUser(userName,tempUser,accountExpiresOn,sftpOnly,userPassword)
    else:
        setupNewUser()
        
if __name__ == '__main__':



```
