Title: Notes - SELinux
Date: 2016-02-15 10:20
Modified: 2016-02-15 10:20
Category: Linux
Tags: selinux
Authors: Craig Riley
Summary: SELinux Notes
#Notes on SELinux

```bash
## Very cool way to find out how to write policy:
##
##  To create a policy using messages from avc:

Use audit2allow, which transforms audit messages from alerts to loadable modules

So, this /var/log/messages alert:
Aug  7 07:22:19 rastamon1 setroubleshoot:      SELinux is preventing /usr/libexec/postfix/local (postfix_local_t) "write" to cricket (mail_spool_t).      For complete SELinux messages. run sealert -l 1afcc5f6-d4a8-47e6-b546-b2ec3b427f18

Shows this in sealert:
[07:25:12 rastamon1] tmp $ sealert -l 1afcc5f6-d4a8-47e6-b546-b2ec3b427f18
Summary
    SELinux is preventing /usr/libexec/postfix/local (postfix_local_t) "write"
    to cricket (mail_spool_t).

Detailed Description
    SELinux denied access requested by /usr/libexec/postfix/local. It is not
    expected that this access is required by /usr/libexec/postfix/local and this
    access may signal an intrusion attempt. It is also possible that the
    specific version or configuration of the application is causing it to
    require additional access.

Allowing Access
    Sometimes labeling problems can cause SELinux denials.  You could try to
    restore the default system file context for cricket, restorecon -v cricket
    If this does not work, there is currently no automatic way to allow this
    access. Instead,  you can generate a local policy module to allow this
    access - see http://fedora.redhat.com/docs/selinux-faq-fc5/#id2961385 Or you
    can disable SELinux protection altogether. Disabling SELinux protection is
    not recommended. Please file a
    http://bugzilla.redhat.com/bugzilla/enter_bug.cgi against this package.

Additional Information        

Source Context                user_u:system_r:postfix_local_t
Target Context                system_u:object_r:mail_spool_t
Target Objects                cricket [ file ]
Affected RPM Packages         postfix-2.3.3-2 [application]
Policy RPM                    selinux-policy-2.4.6-30.el5
Selinux Enabled               True
Policy Type                   targeted
MLS Enabled                   True
Enforcing Mode                Enforcing
Plugin Name                   plugins.catchall_file
Host Name                     rastamon1
Platform                      Linux rastamon1 2.6.18-8.1.6.el5 #1 SMP Fri Jun 1
                              18:52:13 EDT 2007 x86_64 x86_64
Alert Count                   7676
Line Numbers                  

Raw Audit Messages            

avc: denied { write } for comm="local" dev=dm-1 egid=650 euid=650
exe="/usr/libexec/postfix/local" exit=-13 fsgid=650 fsuid=650 gid=0 items=0
name="cricket" pid=25939 scontext=user_u:system_r:postfix_local_t:s0 sgid=0
subj=user_u:system_r:postfix_local_t:s0 suid=0 tclass=file
tcontext=system_u:object_r:mail_spool_t:s0 tty=(none) uid=0

# Basically, postfix can't write to /var/spool/mail/cricket
[07:26:30 rastamon1] tmp $ ls -alZ /var/spool/mail/
drwxrwxr-x  root     mail system_u:object_r:mail_spool_t   .
drwxr-xr-x  root     root system_u:object_r:var_spool_t    ..
-rw-------  cricket  mail system_u:object_r:mail_spool_t   cricket
-rw-------  maorstea mail system_u:object_r:mail_spool_t   maorstea
-rw-------  rfitch   mail system_u:object_r:mail_spool_t   rfitch
-rw-------  root     root system_u:object_r:mail_spool_t   root

# So run audit2allow, and generate a te file:
[07:36:29 rastamon1] tmp $ sudo audit2allow -a -m postfixlocal > postfixlocal.te
[07:37:22 rastamon1] tmp $ cat postfixlocal.te 
module postfixlocal 1.0;

require {
        class file write;
        type mail_spool_t; 
        type postfix_local_t; 
        role system_r; 
};

allow postfix_local_t mail_spool_t:file write;

# And compile it:
[07:37:25 rastamon1] tmp $ sudo checkmodule -M -m -o postfixlocal.mod postfixlocal.te
checkmodule:  loading policy configuration from postfixlocal.te
checkmodule:  policy configuration loaded
checkmodule:  writing binary representation (version 6) to postfixlocal.mod

# and create a policy package:
[07:37:47 rastamon1] tmp $ semodule_package -o postfixlocal.pp -m postfixlocal.mod

# Now we have the ingredients:
[07:38:39 rastamon1] tmp $ file postfixlo*
postfixlocal.mod: data
postfixlocal.pp:  data
postfixlocal.te:  ASCII C++ program text

# Load the policy to the kernel
[07:38:46 rastamon1] tmp $ sudo semodule -i postfixlocal.pp
cricket homedir /usr/local/monitoring or its parent directory conflicts with a
defined context in /etc/selinux/targeted/contexts/files/file_contexts,
/usr/sbin/genhomedircon will not create a new context. This usually indicates an incorrectly defined system account.  If it is a system account please make sure its login shell is /sbin/nologin.

## The above messages did not interfere with the load of the policy:
[07:44:14 rastamon1] / $ sudo semodule -l
amavis  1.1.0
ccs     1.0.0
clamav  1.1.0
dcc     1.1.0
evolution       1.1.0
iscsid  1.0.0
mozilla 1.1.0
mplayer 1.1.0
nagios  1.1.0
oddjob  1.0.1
pcscd   1.0.0
postfixlocal    1.0    <------------   module loaded  =]
pyzor   1.1.0
razor   1.1.0
ricci   1.0.0
smartmon        1.1.0

## Also, we can load the module to another server:
[07:47:50 rastamon1] tmp $ scp postfixlocal.pp rastamon2:/var/tmp
maorstea@rastamon2's password: 
postfixlocal.pp                                                        100% 1017     1.0KB/s   00:00  

[07:48:37 rastamon2] tmp $ sudo semodule -i postfixlocal.pp 
Password:
cricket homedir /usr/local/monitoring or its parent directory conflicts with a
defined context in /etc/selinux/targeted/contexts/files/file_contexts,
/usr/sbin/genhomedircon will not create a new context. This usually indicates an incorrectly defined system account.  If it is a system account please make sure its login shell is /sbin/nologin.

[07:49:02 rastamon2] tmp $ sudo semodule -l |grep postfixlocal
postfixlocal    1.0



### From audit2allow man page:
[Note]  Important
In order to load this newly created policy package into the kernel, you are required to 
execute semodule -i local.pp 
Note that if you later install another module called local, it will replace this module. 
If you want to keep these rules around, then you either need to append future customizations 
to this local.te, or give future customizations a different name. 



###
### Following installation of 5.1 patches (new security pol files)   Received the following messages from
### various commands:

[12:27:52 kroker] ~ $ ssh localhost
/etc/selinux/targeted/contexts/files/file_contexts: Multiple same specifications for /usr/local/lost\+found/.*.
/etc/selinux/targeted/contexts/files/file_contexts: Multiple same specifications for /usr/local/\.journal.
/etc/selinux/targeted/contexts/files/file_contexts: Multiple same specifications for /usr/local/lost\+found.


##  Now, the  file above: file_contexts had no dups, but there were duplicate entries between it and
## the sister file file_contextx.homedirs

### removed the following from the homedirs files:
/usr/local/\.journal    <<none>>
/usr/local/lost\+found  -d      system_u:object_r:lost_found_t:s0
/usr/local/lost\+found/.*       <<none>>

## that worked, no need to restart restorecond

#### Now - separate issue:   ssh borken
##
here's what was updated
[13:06:23 kroker] log # grep ssh /var/log/yum.log 
Nov 14 09:45:03 Updated: openssh.x86_64 4.3p2-24.el5
Nov 14 09:46:54 Updated: openssh-askpass.x86_64 4.3p2-24.el5
Nov 14 09:46:54 Updated: openssh-clients.x86_64 4.3p2-24.el5
Nov 14 09:46:54 Updated: openssh-server.x86_64 4.3p2-24.el5

##after checking a bunch of ssh files, from rpm -ql on the installed packages, removed all openssh 
## and then installed the earlier version, and then it worked.

```
