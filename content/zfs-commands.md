Title: Notes - ZFS Commands
Date: 2016-02-15 10:20
Modified: 2016-02-15 10:20
Category: Unix
Tags: zfs, solaris
Authors: Craig Riley
Summary: Notes from Mike O with some additions from me :)

#ZFS Basic commands
```bash
##
## External resources:
http://www.solarisinternals.com/wiki/index.php/ZFS_Best_Practices_Guide

##
## Create a file system in an existing pool:

[07:02:40 nxdev2] ~ $ zpool list
NAME                    SIZE    USED   AVAIL    CAP  HEALTH     ALTROOT
tank                     68G   21.5G   46.5G    31%  ONLINE     -

[07:02:43 nxdev2] ~ $ zfs list
NAME                   USED  AVAIL  REFER  MOUNTPOINT
tank                  21.5G  45.4G  24.5K  /tank
tank/db01             3.28G  45.4G  3.28G  /db01
tank/twtc             18.2G  45.4G  28.5K  /twtc
tank/twtc/nxvsm       13.7G  45.4G  13.7G  /twtc/nxvsm
tank/twtc/nxvsmac     2.21G  45.4G  2.21G  /twtc/nxvsmac
tank/twtc/nxvsmgc     2.32G  45.4G  2.32G  /twtc/nxvsmgc

### Create a new zfs file system - for /export/home/  500m quota on the fs
sudo zfs create tank/exhome
sudo zfs create tank/exhome/awood
sudo zfs set mountpoint=/export/home tank/exhome
sudo zfs set quota=100m tank/exhome/awood
sudo zfs set quota=500m tank/exhome


[07:13:24 nxdev2] ~ $ zfs list
NAME                   USED  AVAIL  REFER  MOUNTPOINT
tank                  21.5G  45.4G  24.5K  /tank
tank/db01             3.28G  45.4G  3.28G  /db01
tank/exhome           51.5K   500M  25.5K  /export/home
tank/exhome/awood       26K   100M    26K  /export/home/awood
tank/twtc             18.2G  45.4G  28.5K  /twtc
tank/twtc/nxvsm       13.7G  45.4G  13.7G  /twtc/nxvsm
tank/twtc/nxvsmac     2.21G  45.4G  2.21G  /twtc/nxvsmac
tank/twtc/nxvsmgc     2.32G  45.4G  2.32G  /twtc/nxvsmgc

[08:29:31 nxdev2] share $ zfs list tank/exhome tank/exhome/awood
NAME                   USED  AVAIL  REFER  MOUNTPOINT
tank/exhome           51.5K   500M  25.5K  /export/home
tank/exhome/awood       26K   100M    26K  /export/home/awood


#### Use zfs status to show the disks that make up a pool:
[08:30:54 nxdev2] share $ zpool status tank
  pool: tank
 state: ONLINE
 scrub: scrub completed with 0 errors on Mon Dec  3 07:23:04 2007
config:

        NAME        STATE     READ WRITE CKSUM
        tank        ONLINE       0     0     0
          mirror    ONLINE       0     0     0
            c1t2d0  ONLINE       0     0     0
            c1t3d0  ONLINE       0     0     0

errors: No known data errors


## To initiate a block scrub to check for errors, run:
sudo zpool scrub tank

## Snapshots:
    # set up compression:
    sudo zfs set compression=on tank/exhome

    # show some of the filesystem attributes:
    [08:35:05 nxdev2] share $ zfs get compression,quota  tank/exhome
    NAME             PROPERTY       VALUE                      SOURCE
    tank/exhome      compression    on                         local            
    tank/exhome      quota          500M                       local

    # to show all, hey, use 'all'  --->    zfs show all tank/exhome

    # create a snap shot, with just the changes today.

    [08:39:10 nxdev2] share $ sudo zfs snapshot tank/exhome@snap1
    [08:42:39 nxdev2] share $ zfs list
    NAME                   USED  AVAIL  REFER  MOUNTPOINT
    tank                  21.5G  45.4G  24.5K  /tank
    tank/db01             3.28G  45.4G  3.28G  /db01
    tank/exhome           51.5K   500M  25.5K  /export/home
    tank/exhome@snap1         0      -  25.5K  -
    tank/exhome/awood       26K   100M    26K  /export/home/awood
    tank/twtc             18.2G  45.4G  28.5K  /twtc
    tank/twtc/nxvsm       13.7G  45.4G  13.7G  /twtc/nxvsm
    tank/twtc/nxvsmac     2.21G  45.4G  2.21G  /twtc/nxvsmac
    tank/twtc/nxvsmgc     2.32G  45.4G  2.32G  /twtc/nxvsmgc

    [08:42:41 nxdev2] share $ ls -al /export/home/.
    ./  ../ 

    # the snapshot is empty - no files were there
```

#ZFS Root
```bash
# documenting steps to setup zfs root via jumpstart. 

## TODO testing:

play with boot -Z from PROM - list datasets
play with boot -L from PROM - list BE's
boot alternate disk
    validate path with prtconf -vp |grep bootpath

test primary disk failure... this is a potential 'con'.   if the primary mirror disk fails, 
we'll need to take downtime to repair.   Architecturally, this means maybe we should consider 
3 disk mirrors.   *Action - contact SUN to find out plan for this not being an issue (hot-swap 
of primary root disk)

test adding a 3rd mirror-disk

play with root snapshots 
    - send to NFS or other server... 
    - roll back local ; roll back NFS
    - bare-metal restore to alt hardware (DR)

## Considerations:
-Any non-root zfs file systems we want need to be created early in the JS cycle, if they are for 
 post JS install (such as creating /export/home early in a separate zpool)

--Due to CR 6724860, you must run savecore manually to save a crash dump when using a
ZFS dump volume.  (check with Conrad Geiger re: this)



## Here's the extent of the modifications to the profile (first run):
    [08:58:40 infraprdapp01] PROFILES $ diff pststapp01.profile pststapp01.profile.orig_jumpstart 
    5,6c5,11
    < pool rootpool auto auto auto mirror c1t0d0s0 c1t1d0s0
    < bootenv installbe bename zfsroot dataset /var
    ---
    > partitioning explicit
    > filesys mirror:d10 c1t0d0s0 c1t1d0s0 10240 /
    > filesys mirror:d20 c1t0d0s1 c1t1d0s1 32768 swap
    > filesys mirror:d30 c1t0d0s3 c1t1d0s3 12288 /var
    > filesys mirror:d40 c1t0d0s4 c1t1d0s4 12288 /export/home
    > metadb c1t0d0s7 size 8192 count 3
    > metadb c1t1d0s7 size 8192 count 3


## The allocations above automatically partitioned a full slice 0 on the two disks.
## If additional devices are added later, they will prolly need to be explicitly partitioned

## By running zfs history, post-install, we can see the commands that were run to create the 
## root zpool:

    -bash-3.00# zpool history
    History for 'rootpool':
    2009-07-09.07:54:43 zpool create -f -o failmode=continue -R /a -m legacy -o cachefile=/tmp/root/etc/zfs/zpool.cache rootpool mirror c1t0d0s0 c1t1d0s0
    2009-07-09.07:54:44 zfs set canmount=noauto rootpool
    2009-07-09.07:54:45 zfs set mountpoint=/rootpool rootpool
    2009-07-09.07:54:45 zfs create -o mountpoint=legacy rootpool/ROOT
    2009-07-09.07:54:46 zfs create -b 8192 -V 2048m rootpool/swap
    2009-07-09.07:54:47 zfs create -b 131072 -V 1536m rootpool/dump
    2009-07-09.07:55:06 zfs create -o canmount=noauto rootpool/ROOT/zfsroot
    2009-07-09.07:55:07 zfs create -o canmount=noauto rootpool/ROOT/zfsroot/var
    2009-07-09.07:55:08 zpool set bootfs=rootpool/ROOT/zfsroot rootpool
    2009-07-09.07:55:09 zfs set mountpoint=/ rootpool/ROOT/zfsroot
    2009-07-09.07:55:09 zfs set canmount=on rootpool
    2009-07-09.07:55:10 zfs create -o mountpoint=/export rootpool/export
    2009-07-09.07:55:11 zfs create rootpool/export/home


## The ZFS pool version:
    -bash-3.00# zpool upgrade
    This system is currently running ZFS pool version 10.

    All pools are formatted using this version.


## Post install, here's what everything looked like:

    -bash-3.00# zpool list  
    NAME       SIZE   USED  AVAIL    CAP  HEALTH  ALTROOT
    rootpool   136G  4.14G   132G     3%  ONLINE  -

    -bash-3.00# zpool status
      pool: rootpool
     state: ONLINE
     scrub: none requested
    config:

            NAME          STATE     READ WRITE CKSUM
            rootpool      ONLINE       0     0     0
              mirror      ONLINE       0     0     0
                c1t0d0s0  ONLINE       0     0     0
                c1t1d0s0  ONLINE       0     0     0

    errors: No known data errors

    -bash-3.00# zfs list
    NAME                        USED  AVAIL  REFER  MOUNTPOINT
    rootpool                   6.14G   128G    94K  /rootpool
    rootpool/ROOT              2.63G   128G    18K  legacy
    rootpool/ROOT/zfsroot      2.63G   128G  2.43G  /
    rootpool/ROOT/zfsroot/var   214M   128G   214M  /var
    rootpool/dump              1.50G   128G  1.50G  -
    rootpool/export              38K   128G    20K  /export
    rootpool/export/home         18K   128G    18K  /export/home
    rootpool/swap                 2G   130G    16K  -

    ## Note that the default sizing for swap and dump sized them at 2G and 1.5G respectively:
    pool rootpool auto auto auto mirror c1t0d0s0 c1t1d0s0
    (It's the 2nd and 3rd "auto's" ) that size them



    -bash-3.00# swap -l
    swapfile             dev  swaplo blocks   free
    /dev/zvol/dsk/rootpool/swap 256,2      16 4194288 4194288

    -bash-3.00# dumpadm
          Dump content: kernel pages
           Dump device: /dev/zvol/dsk/rootpool/dump (dedicated)
    Savecore directory: /var/crash/pststapp01
      Savecore enabled: yes


    ## The default settings for the root filesystem:
    
    -- The BE info:
    ---------------
    -bash-3.00# lustatus
    Boot Environment           Is       Active Active    Can    Copy      
    Name                       Complete Now    On Reboot Delete Status    
    -------------------------- -------- ------ --------- ------ ----------
    zfsroot                    yes      yes    yes       no     -         
    -bash-3.00# lucurr
    zfsroot

    -- The zfs settings for root for that BE:
    command notes: 
        zfs get -r (recursive) "all"|property[,...] fs|vol|snapshot
    
    -bash-3.00# zfs get -r all  rootpool/ROOT/zfsroot
    NAME                       PROPERTY         VALUE                  SOURCE
    rootpool/ROOT/zfsroot      type             filesystem             -
    rootpool/ROOT/zfsroot      creation         Thu Jul  9  7:55 2009  -
    rootpool/ROOT/zfsroot      used             2.64G                  -
    rootpool/ROOT/zfsroot      available        128G                   -
    rootpool/ROOT/zfsroot      referenced       2.43G                  -
    rootpool/ROOT/zfsroot      compressratio    1.00x                  -
    rootpool/ROOT/zfsroot      mounted          yes                    -
    rootpool/ROOT/zfsroot      quota            none                   default
    rootpool/ROOT/zfsroot      reservation      none                   default
    rootpool/ROOT/zfsroot      recordsize       128K                   default
    rootpool/ROOT/zfsroot      mountpoint       /                      local
    rootpool/ROOT/zfsroot      sharenfs         off                    default
    rootpool/ROOT/zfsroot      checksum         on                     default
    rootpool/ROOT/zfsroot      compression      off                    default
    rootpool/ROOT/zfsroot      atime            on                     default
    rootpool/ROOT/zfsroot      devices          on                     default
    rootpool/ROOT/zfsroot      exec             on                     default
    rootpool/ROOT/zfsroot      setuid           on                     default
    rootpool/ROOT/zfsroot      readonly         off                    default
    rootpool/ROOT/zfsroot      zoned            off                    default
    rootpool/ROOT/zfsroot      snapdir          hidden                 default
    rootpool/ROOT/zfsroot      aclmode          groupmask              default
    rootpool/ROOT/zfsroot      aclinherit       restricted             default
    rootpool/ROOT/zfsroot      canmount         noauto                 local
    rootpool/ROOT/zfsroot      shareiscsi       off                    default
    rootpool/ROOT/zfsroot      xattr            on                     default
    rootpool/ROOT/zfsroot      copies           1                      default
    rootpool/ROOT/zfsroot      version          3                      -
    rootpool/ROOT/zfsroot      utf8only         off                    -
    rootpool/ROOT/zfsroot      normalization    none                   -
    rootpool/ROOT/zfsroot      casesensitivity  sensitive              -
    rootpool/ROOT/zfsroot      vscan            off                    default
    rootpool/ROOT/zfsroot      nbmand           off                    default
    rootpool/ROOT/zfsroot      sharesmb         off                    default
    rootpool/ROOT/zfsroot      refquota         none                   default
    rootpool/ROOT/zfsroot      refreservation   none                   default
    rootpool/ROOT/zfsroot/var  type             filesystem             -
    rootpool/ROOT/zfsroot/var  creation         Thu Jul  9  7:55 2009  -
    rootpool/ROOT/zfsroot/var  used             215M                   -
    rootpool/ROOT/zfsroot/var  available        128G                   -
    rootpool/ROOT/zfsroot/var  referenced       215M                   -
    rootpool/ROOT/zfsroot/var  compressratio    1.00x                  -
    rootpool/ROOT/zfsroot/var  mounted          yes                    -
    rootpool/ROOT/zfsroot/var  quota            none                   default
    rootpool/ROOT/zfsroot/var  reservation      none                   default
    rootpool/ROOT/zfsroot/var  recordsize       128K                   default
    rootpool/ROOT/zfsroot/var  mountpoint       /var                   inherited from rootpool/ROOT/zfsroot
    rootpool/ROOT/zfsroot/var  sharenfs         off                    default
    rootpool/ROOT/zfsroot/var  checksum         on                     default
    rootpool/ROOT/zfsroot/var  compression      off                    default
    rootpool/ROOT/zfsroot/var  atime            on                     default
    rootpool/ROOT/zfsroot/var  devices          on                     default
    rootpool/ROOT/zfsroot/var  exec             on                     default
    rootpool/ROOT/zfsroot/var  setuid           on                     default
    rootpool/ROOT/zfsroot/var  readonly         off                    default
    rootpool/ROOT/zfsroot/var  zoned            off                    default
    rootpool/ROOT/zfsroot/var  snapdir          hidden                 default
    rootpool/ROOT/zfsroot/var  aclmode          groupmask              default
    rootpool/ROOT/zfsroot/var  aclinherit       restricted             default
    rootpool/ROOT/zfsroot/var  canmount         noauto                 local
    rootpool/ROOT/zfsroot/var  shareiscsi       off                    default
    rootpool/ROOT/zfsroot/var  xattr            on                     default
    rootpool/ROOT/zfsroot/var  copies           1                      default
    rootpool/ROOT/zfsroot/var  version          3                      -
    rootpool/ROOT/zfsroot/var  utf8only         off                    -
    rootpool/ROOT/zfsroot/var  normalization    none                   -
    rootpool/ROOT/zfsroot/var  casesensitivity  sensitive              -
    rootpool/ROOT/zfsroot/var  vscan            off                    default
    rootpool/ROOT/zfsroot/var  nbmand           off                    default
    rootpool/ROOT/zfsroot/var  sharesmb         off                    default
    rootpool/ROOT/zfsroot/var  refquota         none                   default
    rootpool/ROOT/zfsroot/var  refreservation   none                   default
        

    ## Items of note:
    no compression:
    rootpool/ROOT/zfsroot      compression      off                    default

    no sharenfs:
    rootpool/ROOT/zfsroot      sharenfs         off                    default

    checksum is on:
    rootpool/ROOT/zfsroot      checksum         on                     default

    no size restrictions:
    rootpool/ROOT/zfsroot/var  quota            none                   default
    rootpool/ROOT/zfsroot/var  reservation      none                   default

    rootpool/ROOT/zfsroot/var  refquota         none                   default
    rootpool/ROOT/zfsroot/var  refreservation   none                   default

## And the disk partitioning:
    -bash-3.00# prtvtoc /dev/rdsk/c1t0d0s0
    * /dev/rdsk/c1t0d0s0 partition map
    *
    * Dimensions:
    *     512 bytes/sector
    *     848 sectors/track
    *      24 tracks/cylinder
    *   20352 sectors/cylinder
    *   14089 cylinders
    *   14087 accessible cylinders
    *
    * Flags:
    *   1: unmountable
    *  10: read-only
    *
    *                          First     Sector    Last
    * Partition  Tag  Flags    Sector     Count    Sector  Mount Directory
           0      2    00          0 286698624 286698623
           2      5    00          0 286698624 286698623


    -bash-3.00# prtvtoc /dev/rdsk/c1t1d0s0
    * /dev/rdsk/c1t1d0s0 partition map
    *
    * Dimensions:
    *     512 bytes/sector
    *     848 sectors/track
    *      24 tracks/cylinder
    *   20352 sectors/cylinder
    *   14089 cylinders
    *   14087 accessible cylinders
    *
    * Flags:
    *   1: unmountable
    *  10: read-only
    *
    *                          First     Sector    Last
    * Partition  Tag  Flags    Sector     Count    Sector  Mount Directory
           0      0    00          0 286698624 286698623
           2      5    00          0 286698624 286698623

    
### Now, let's setup some resource limitations:

10GB quota for /var:
    -bash-3.00# zfs set quota=10g rootpool/ROOT/zfsroot/var

    -bash-3.00# zfs list -o name,used,avail,refer,quota rootpool/ROOT/zfsroot/var
    NAME                        USED  AVAIL  REFER  QUOTA
    rootpool/ROOT/zfsroot/var   283M  9.72G   283M    10G

    -bash-3.00# df -h
    Filesystem             size   used  avail capacity  Mounted on
    rootpool/ROOT/zfsroot
                           134G   2.4G   128G     2%    /
    /devices                 0K     0K     0K     0%    /devices
    ctfs                     0K     0K     0K     0%    /system/contract
    proc                     0K     0K     0K     0%    /proc
    mnttab                   0K     0K     0K     0%    /etc/mnttab
    swap                    28G   1.2M    28G     1%    /etc/svc/volatile
    objfs                    0K     0K     0K     0%    /system/object
    sharefs                  0K     0K     0K     0%    /etc/dfs/sharetab
    /platform/SUNW,SPARC-Enterprise-T5220/lib/libc_psr/libc_psr_hwcap2.so.1
                           130G   2.4G   128G     2%    /platform/sun4v/lib/libc_psr.so.1
    /platform/SUNW,SPARC-Enterprise-T5220/lib/sparcv9/libc_psr/libc_psr_hwcap2.so.1
                           130G   2.4G   128G     2%    /platform/sun4v/lib/sparcv9/libc_psr.so.1
    fd                       0K     0K     0K     0%    /dev/fd
    rootpool/ROOT/zfsroot/var
                            10G   283M   9.7G     3%    /var    <-------------------
    swap                    28G    96K    28G     1%    /tmp
    swap                    28G    32K    28G     1%    /var/run
    rootpool/export        134G    20K   128G     1%    /export
    rootpool/export/home   134G    18K   128G     1%    /export/home
    rootpool               134G    94K   128G     1%    /rootpool


10G reserved for / (not including snaps)

    -bash-3.00# df -h /
    Filesystem             size   used  avail capacity  Mounted on
    rootpool/ROOT/zfsroot
                           134G   2.4G   128G     2%    /

    -bash-3.00# zfs list /
    NAME                    USED  AVAIL  REFER  MOUNTPOINT
    rootpool/ROOT/zfsroot  2.70G   128G  2.43G  /

    -bash-3.00# zfs set refreservation=10g rootpool/ROOT/zfsroot
    -bash-3.00# zfs list /
    NAME                    USED  AVAIL  REFER  MOUNTPOINT
    rootpool/ROOT/zfsroot  10.3G   128G  2.43G  /


## Now, let's take a snapshot of / only
    -bash-3.00# zfs snapshot rootpool/ROOT/zfsroot@20090714a
    -bash-3.00# zfs list -r /
    NAME                              USED  AVAIL  REFER  MOUNTPOINT
    rootpool/ROOT/zfsroot            12.7G   128G  2.43G  /
    rootpool/ROOT/zfsroot@20090714a      0      -  2.43G  -
    rootpool/ROOT/zfsroot/var         283M  9.72G   283M  /var

    -bash-3.00# zfs get all rootpool/ROOT/zfsroot@20090714a
    NAME                             PROPERTY         VALUE                  SOURCE
    rootpool/ROOT/zfsroot@20090714a  type             snapshot               -
    rootpool/ROOT/zfsroot@20090714a  creation         Tue Jul 14 22:04 2009  -
    rootpool/ROOT/zfsroot@20090714a  used             0                      -
    rootpool/ROOT/zfsroot@20090714a  referenced       2.43G                  -
    rootpool/ROOT/zfsroot@20090714a  compressratio    1.00x                  -
    rootpool/ROOT/zfsroot@20090714a  devices          on                     default
    rootpool/ROOT/zfsroot@20090714a  exec             on                     default
    rootpool/ROOT/zfsroot@20090714a  setuid           on                     default
    rootpool/ROOT/zfsroot@20090714a  shareiscsi       off                    default
    rootpool/ROOT/zfsroot@20090714a  xattr            on                     default
    rootpool/ROOT/zfsroot@20090714a  version          3                      -
    rootpool/ROOT/zfsroot@20090714a  utf8only         off                    -
    rootpool/ROOT/zfsroot@20090714a  normalization    none                   -
    rootpool/ROOT/zfsroot@20090714a  casesensitivity  sensitive              -
    rootpool/ROOT/zfsroot@20090714a  nbmand           off                    default

    -bash-3.00# ls -al /.zfs
    total 5
    dr-xr-xr-x   3 root     root           3 Jul  9 07:55 .
    drwxr-xr-x  26 root     root          29 Jul 14 14:19 ..
    dr-xr-xr-x   2 root     root           2 Jul  9 07:55 snapshot

## Recover a file:
    -bash-3.00# cat /etc/motd
    Sun Microsystems Inc.   SunOS 5.10      Generic January 2005
    -bash-3.00# echo 'mike o is da bomb!' > /etc/motd
    -bash-3.00# cat /etc/motd
    mike o is da bomb!
    -bash-3.00# cp /.zfs/snapshot/20090714a/etc/motd /etc/motd
    -bash-3.00# cat /etc/motd
    Sun Microsystems Inc.   SunOS 5.10      Generic January 2005

## and, now that the dataset changed (regardless of the data returning to original data), 
## the size of the snapshot has changed:
    -bash-3.00# zfs list -r /
    NAME                              USED  AVAIL  REFER  MOUNTPOINT
    rootpool/ROOT/zfsroot            12.7G   128G  2.43G  /
    rootpool/ROOT/zfsroot@20090714a  38.5K      -  2.43G  -    <----------
    rootpool/ROOT/zfsroot/var         283M  9.72G   283M  /var

##  Now, let's create a recursive snapshot of /, which will include it's dependencies:
    -bash-3.00# zfs snapshot -r rootpool/ROOT/zfsroot@20090714b
    -bash-3.00# zfs list -r /
    NAME                                  USED  AVAIL  REFER  MOUNTPOINT
    rootpool/ROOT/zfsroot                12.7G   128G  2.43G  /
    rootpool/ROOT/zfsroot@20090714a      38.5K      -  2.43G  -
    rootpool/ROOT/zfsroot@20090714b          0      -  2.43G  -
    rootpool/ROOT/zfsroot/var             283M  9.72G   283M  /var
    rootpool/ROOT/zfsroot/var@20090714b      0      -   283M  -

    # note that /var and / zfs filesystems both have a snapshot named the same.

## Here's all the snapshots:
    -bash-3.00# zfs list -t snapshot -r -o name,creation /
    NAME                                 CREATION
    rootpool/ROOT/zfsroot@20090714a      Tue Jul 14 22:04 2009
    rootpool/ROOT/zfsroot@20090714b      Tue Jul 14 22:14 2009
    rootpool/ROOT/zfsroot/var@20090714b  Tue Jul 14 22:14 2009


## dump and swap:
    -bash-3.00# dumpadm      
          Dump content: kernel pages
           Dump device: /dev/zvol/dsk/rootpool/dump (dedicated)
    Savecore directory: /var/crash/pststapp01
      Savecore enabled: yes

    -bash-3.00# swap -l
    swapfile             dev  swaplo blocks   free
    /dev/zvol/dsk/rootpool/swap 256,2      16 4194288 4194288


    ## and the devices:
    -bash-3.00# ls -al   /dev/zvol/dsk/rootpool/
    total 8
    drwxr-xr-x   2 root     root           4 Jul  9 08:19 .
    drwxr-xr-x   3 root     root           3 Jul  9 08:08 ..
    lrwxrwxrwx   1 root     root          35 Jul  9 08:19 dump -> ../../../../devices/pseudo/zfs@0:1c
    lrwxrwxrwx   1 root     root          35 Jul  9 08:19 swap -> ../../../../devices/pseudo/zfs@0:2c

    -bash-3.00# zfs get all rootpool/dump rootpool/swap
    NAME           PROPERTY         VALUE                  SOURCE
    rootpool/dump  type             volume                 -
    rootpool/dump  creation         Thu Jul  9  7:54 2009  -
    rootpool/dump  used             1.50G                  -
    rootpool/dump  available        118G                   -
    rootpool/dump  referenced       1.50G                  -
    rootpool/dump  compressratio    1.00x                  -
    rootpool/dump  reservation      none                   default
    rootpool/dump  volsize          1.50G                  -
    rootpool/dump  volblocksize     128K                   -
    rootpool/dump  checksum         off                    local
    rootpool/dump  compression      off                    local
    rootpool/dump  readonly         off                    default
    rootpool/dump  shareiscsi       off                    default
    rootpool/dump  copies           1                      default
    rootpool/dump  refreservation   none                   default
    rootpool/swap  type             volume                 -
    rootpool/swap  creation         Thu Jul  9  7:54 2009  -
    rootpool/swap  used             2G                     -
    rootpool/swap  available        120G                   -
    rootpool/swap  referenced       16K                    -
    rootpool/swap  compressratio    1.00x                  -
    rootpool/swap  reservation      none                   default
    rootpool/swap  volsize          2G                     -
    rootpool/swap  volblocksize     8K                     -
    rootpool/swap  checksum         on                     default
    rootpool/swap  compression      off                    default
    rootpool/swap  readonly         off                    default
    rootpool/swap  shareiscsi       off                    default
    rootpool/swap  copies           1                      default
    rootpool/swap  refreservation   2G                     local

## Resize dump device and swap to 4g each

    #  Resize Dump
    -bash-3.00# zfs list rootpool/dump
    NAME            USED  AVAIL  REFER  MOUNTPOINT
    rootpool/dump  1.50G   118G  1.50G  -

    -bash-3.00# zfs get volsize  rootpool/dump
    NAME           PROPERTY  VALUE          SOURCE
    rootpool/dump  volsize   1.50G          -

    -bash-3.00# zfs set volsize=4g  rootpool/dump

    -bash-3.00# zfs get volsize  rootpool/dump
    NAME           PROPERTY  VALUE          SOURCE
    rootpool/dump  volsize   4G             -

    -bash-3.00# zfs list rootpool/dump 
    NAME            USED  AVAIL  REFER  MOUNTPOINT
    rootpool/dump  4.00G   115G  4.00G  -


    # resize swap:
    -bash-3.00# zfs list rootpool/swap 
    NAME            USED  AVAIL  REFER  MOUNTPOINT
    rootpool/swap     2G   117G    16K  -

    -bash-3.00# swap -l               
    swapfile             dev  swaplo blocks   free
    /dev/zvol/dsk/rootpool/swap 256,2      16 4194288 4194288

    # remove the swap space
    -bash-3.00# swap -d /dev/zvol/dsk/rootpool/swap

    -bash-3.00# swap -l
    No swap devices configured

    # grow the swap zfs volume
    -bash-3.00# zfs set volsize=4g rootpool/swap

    -bash-3.00# zfs get volsize rootpool/swap
    NAME           PROPERTY  VALUE          SOURCE
    rootpool/swap  volsize   4G             -

    # re-add the swap device
    -bash-3.00# swap -a /dev/zvol/dsk/rootpool/swap
    /dev/zvol/dsk/rootpool/swap is in use for live upgrade -. Please see ludelete(1M).

    # so, use swapadd instead
    -bash-3.00# /sbin/swapadd
    -bash-3.00# swap -l
    swapfile             dev  swaplo blocks   free
    /dev/zvol/dsk/rootpool/swap 256,2      16 8388592 8388592

```

#ZFS Boot Environment and Live Upgrade
```bash
## Tasks:
create a second BE (lucreate)
patch the second BE with latest patches (luupgrade)
make the 2nd BE bootable and active on next reboot (luactivate)
compare the changed files across the BE's (lucompare)
mount file systems from the inactive BE (lumount) and umount (luumount)
boot from the new BE (test boot -Z display)
boot again from the 1st BE (simulate roll-back) (luactivate)


## Coniderations:

 Live Upgrade Issues

    * The Solaris installation GUI's standard-upgrade option is not available for migrating from a UFS to a ZFS root 
        file system. To migrate from a UFS file system, you must use Solaris Live Upgrade.
    * You cannot use Solaris Live Upgrade to create a UFS BE from a ZFS BE.
    * Do not rename your ZFS BEs with the zfs rename command because the Solaris Live Upgrade feature is unaware of 
        the name change. Subsequent commands, such as ludelete, will fail. In fact, do not rename your ZFS pools or 
        file systems if you have existing BEs that you want to continue to use.
    * Solaris Live Upgrade creates the datasets for the BE and ZFS volumes for the swap area and dump device but does 
        not account for any existing dataset property modifications. Thus, if you want a dataset property enabled in 
        the new BE, you must set the property before the lucreate operation. For example: 

         zfs set compression=on rpool/ROOT

    * When creating an alternative BE that is a clone of the primary BE, you cannot use the -f, -x, -y, -Y, and -z 
        options to include or exclude files from the primary BE. You can still use the inclusion and exclusion option 
        set in the following cases: 

        UFS -> UFS UFS -> ZFS ZFS -> ZFS (different pool)

    * Although you can use Solaris Live Upgrade to upgrade your UFS root file system to a ZFS root file system, you 
            cannot use Solaris Live Upgrade to upgrade non-root or shared file systems.
    * On a SPARC system that runs the Solaris 10 5/09 release, set the BOOT_MENU_FILE variable before activating the 
        ZFS BE with luactivate, due to CR 6824589. 

        # BOOT_MENU_FILE="menu.lst"
        # export BOOT_MENU_FILE


## starting zfs environment:

    -bash-3.00# zfs list
    NAME                                  USED  AVAIL  REFER  MOUNTPOINT
    rootpool                             20.8G   113G    94K  /rootpool
    rootpool/ROOT                        12.8G   113G    18K  legacy
    rootpool/ROOT/zfsroot                12.8G   123G  2.43G  /
    rootpool/ROOT/zfsroot@20090714a      38.5K      -  2.43G  -
    rootpool/ROOT/zfsroot@20090714b        38K      -  2.43G  -
    rootpool/ROOT/zfsroot/var             362M  9.65G   361M  /var
    rootpool/ROOT/zfsroot/var@20090714b  1.63M      -   283M  -
    rootpool/dump                        4.00G   113G  4.00G  -
    rootpool/export                        38K   113G    20K  /export
    rootpool/export/home                   18K   113G    18K  /export/home
    rootpool/swap                           4G   117G    16K  -


    -bash-3.00# zpool status
      pool: rootpool
     state: ONLINE
     scrub: none requested
    config:

            NAME          STATE     READ WRITE CKSUM
            rootpool      ONLINE       0     0     0
              mirror      ONLINE       0     0     0
                c1t0d0s0  ONLINE       0     0     0
                c1t1d0s0  ONLINE       0     0     0

    errors: No known data errors

## Starting BE setup:
    -bash-3.00# lustatus
    Boot Environment           Is       Active Active    Can    Copy      
    Name                       Complete Now    On Reboot Delete Status    
    -------------------------- -------- ------ --------- ------ ----------
    zfsroot                    yes      yes    yes       no     -       


    -bash-3.00# cat /etc/lutab
    # DO NOT EDIT THIS FILE BY HAND. This file is not a public interface.
    # The format and contents of this file are subject to change.
    # Any user modification to this file may result in the incorrect
    # operation of Live Upgrade.
    1:zfsroot:C:0
    1:/:rootpool/ROOT/zfsroot:1
    1:boot-device:/dev/dsk/c1t0d0s0:2

    -bash-3.00# lucurr
    zfsroot

## From infodoc 206844, minimum sol10 LU patch levels:

    The following patches provide Live Upgrade functionality for Solaris 10 SPARC:
    If you are running non-global zones, see the subsequent section for additional patches which you must also install.
    118815-05 or higher nawk patch
    120900-04 or higher libzonecfg patch
    121133-02 or higher SUNWzoneu required patch
    119254-64 or higher Install and Patch Utilities Patch**
    119317-01 or higher SVr4 Packaging Commands (usr) patch
    120235-01 or higher SUNWluzone required patches
    121428-08 or higher SUNWluzone required patches
    121002-03 or higher pax patches
    123121-02 or higher prodreg patches
    The following patch is only required if the TSIpgx package is installed:
    119309-03 or higher PGX32 Graphics (TSIpgx Power Management)
    121004-03 or higher sh patch
    119574-02 or higher su patch
    120996-02 or higher cpio patch
    120068-03 or higher telnet security patch
    119042-10 or higher /usr/sbin/svccfg patch
    126538-01 or higher i.manifest r.manifest class action script patch
    123332-01 or higher tftp patch
    119246-27 or higher Man pages patch
    121901-02 or higher i.manifest r.manifest class action script patch
    125418-01 or higher in.telnetd patch
    121430-34 or higher Live Upgrade patch
    123839-07 or higher Fault Manager patch
    127922-03 or higher cpio patch
    137321-01 or higher p7zip patch (required if upgrading to Solaris 10 5/08 or higher)
    138130-01 or higher vold patch
    If applied to the live boot environment, the system should be rebooted once all patches are applied.

    ## All levels validated to exceed those above.

    
    ## But, install the latest patch for Live Upgrade (best practice)
    ## This particular patch addresses the luactivate issue (the work-around of exporting BOOT_MENU_FILE)

    -bash-3.00# patchadd -d 121430-37
    Validating patches...

    Loading patches installed on the system...
    Done!
    Loading patches requested to install.
    Done!
    Checking patches that you specified for installation.
    Done!
    Approved patches will be installed in this order:
    121430-37 
    Checking installed patches...
    Executing prepatch script...
    Verifying sufficient filesystem capacity (dry run method)...
    Installing patch packages...

    Patch 121430-37 has been successfully installed.
    See /var/sadm/patch/121430-37/log for details

    Patch packages installed:
      SUNWlucfg
      SUNWlur
      SUNWluu


## Now, we can start:


## Create the second BE:
    -bash-3.00# lucreate -n 20090721mao
    Analyzing system configuration.
    Comparing source boot environment <zfsroot> file systems with the file 
    system(s) you specified for the new boot environment. Determining which 
    file systems should be in the new boot environment.
    Updating boot environment description database on all BEs.
    Updating system configuration files.
    Creating configuration for boot environment <20090721mao>.
    Source boot environment is <zfsroot>.
    Creating boot environment <20090721mao>.
    Cloning file systems from boot environment <zfsroot> to create boot environment <20090721mao>.
    Creating snapshot for <rootpool/ROOT/zfsroot> on <rootpool/ROOT/zfsroot@20090721mao>.
    Creating clone for <rootpool/ROOT/zfsroot@20090721mao> on <rootpool/ROOT/20090721mao>.
    Setting canmount=noauto for </> in zone <global> on <rootpool/ROOT/20090721mao>.
    Creating snapshot for <rootpool/ROOT/zfsroot/var> on <rootpool/ROOT/zfsroot/var@20090721mao>.
    Creating clone for <rootpool/ROOT/zfsroot/var@20090721mao> on <rootpool/ROOT/20090721mao/var>.
    Setting canmount=noauto for </var> in zone <global> on <rootpool/ROOT/20090721mao/var>.
    Population of boot environment <20090721mao> successful.
    Creation of boot environment <20090721mao> successful.


    -bash-3.00# zfs list
    NAME                                    USED  AVAIL  REFER  MOUNTPOINT
    rootpool                               24.5G   109G    94K  /rootpool
    rootpool/ROOT                          16.5G   109G    18K  legacy
    rootpool/ROOT/20090721mao               145K   109G  2.43G  /               <-----
    rootpool/ROOT/20090721mao/var            50K   109G  4.06G  /var            <-----
    rootpool/ROOT/zfsroot                  16.5G   119G  2.43G  /
    rootpool/ROOT/zfsroot@20090714a        38.5K      -  2.43G  -
    rootpool/ROOT/zfsroot@20090714b          38K      -  2.43G  -
    rootpool/ROOT/zfsroot@20090721mao      69.5K      -  2.43G  -
    rootpool/ROOT/zfsroot/var              4.07G  5.93G  4.06G  /var
    rootpool/ROOT/zfsroot/var@20090714b    10.4M      -   283M  -
    rootpool/ROOT/zfsroot/var@20090721mao   310K      -  4.06G  -               <-----
    rootpool/dump                          4.00G   109G  4.00G  -
    rootpool/export                          38K   109G    20K  /export
    rootpool/export/home                     18K   109G    18K  /export/home
    rootpool/swap                             4G   113G    16K  -


    -bash-3.00# lustatus
    Boot Environment           Is       Active Active    Can    Copy      
    Name                       Complete Now    On Reboot Delete Status    
    -------------------------- -------- ------ --------- ------ ----------
    zfsroot                    yes      yes    yes       no     -         
    20090721mao                yes      no     no        yes    -         



## patch the second BE with latest patches (luupgrade)

    ## patch set copied locally:
    -bash-3.00# ls -lad /var/tmp/10_Recommended
    drwxr-xr-x 157 root     root         161 Jul 17 12:13 /var/tmp/10_Recommended

    ## Usage:
    luupgrade  - Add Patches:     luupgrade -t -n BE_name [ -l error_log ] [ -o outfile ] [ -N ] [ -X ] -s source_patches_path 
        [ -O patchadd_options ] [ patchname [ patchname... ] ]

## Patch:
    -bash-3.00# luupgrade -t -n 20090721mao -s /var/tmp/10_Recommended 

    Validating the contents of the media </var/tmp/10_Recommended>.
    The media contains 155 software patches that can be added.
    All 155 patches will be added because you did not specify any specific patches to add.
    Mounting the BE <20090721mao>.
    Adding patches to the BE <20090721mao>.
    Validating patches...

    Loading patches installed on the system...

    Done!

    Loading patches requested to install.

    Version of package SUNWpfb from directory SUNWpfb.u in patch 118712-23 differs from the package installed on the system.
    Version of package SUNWpfb from directory SUNWpfb.us in patch 118712-23 differs from the package installed on the system.
    Version of package SUNWced from directory SUNWced.us in patch 118777-14 differs from the package installed on the system.
    Version of package SUNWced from directory SUNWced.u in patch 118777-14 differs from the package installed on the system.
    Version of package SUNWkvm from directory SUNWkvm.u in patch 118833-36 differs from the package installed on the system.
    
    ...
    ...


    Requested patch 140860-01 is already installed on the system.
    Requested patch 140899-01 is already installed on the system.
    Requested patch 141016-01 is already installed on the system.

    The following requested patches do not update any packages installed on the system
    No Packages from patch 139943-01 are installed on the system.

    Checking patches that you specified for installation.

    Done!


    The following requested patches will not be installed because
    they have been made obsolete by other patches already
    installed on the system or by patches you have specified for installation.

               0 All packages from patch 118731-01 are patched by higher revision patches.

               1 All packages from patch 122660-10 are patched by higher revision patches.

               2 All packages from patch 124204-04 are patched by higher revision patches.


    The following requested patches will not be installed because
    the packages they patch are not installed on this system.

               0 No Packages from patch 121975-01 are installed on the system.

               1 No Packages from patch 118667-19 are installed on the system.

    ...
    ...


    
    The following requested patches will not be installed because
    at least one required patch is not installed on this system.

               0 For patch 120410-31, required patch 121975-01 will not be installed because it updates no packages on this system.

    Approved patches will be installed in this order:

    118666-20 118777-14 118959-04 119059-47 119090-32 119213-19 119254-66 119757-15 
    119783-11 120272-24 122261-02 122911-16 123893-15 125555-05 125952-19 137080-03 
    138322-03 138822-04 138874-03 139604-05 139606-02 139608-04 139966-02 139969-02 
    140074-08 140171-02 140386-04 140391-03 140397-08 140917-01 140921-01 141020-01 
    141414-02 141719-01 141733-03 141742-02 141765-01 141778-02 


    Checking installed patches...
    Verifying sufficient filesystem capacity (dry run method)...
    Installing patch packages...
   


## While patching:
    
    -bash-3.00# ps -eaf |grep luu
    root 16270 15416   0 14:33:12 pts/2       0:00 grep luu
    root  2434 28299   0 14:30:50 pts/1       0:01 /bin/ksh /usr/sbin/luupgrade -t -n 20090721mao -s /var/tmp/10_Recommended

    -bash-3.00# lustatus
    Boot Environment           Is       Active Active    Can    Copy      
    Name                       Complete Now    On Reboot Delete Status    
    -------------------------- -------- ------ --------- ------ ----------
    zfsroot                    yes      yes    yes       no     -         
    20090721mao                yes      no     no        yes    -         

    -bash-3.00# ptree 2434 
    415   /opt/quest/sbin/sshd
      28296 /opt/quest/sbin/sshd -R
        28299 -bash
          2434  /bin/ksh /usr/sbin/luupgrade -t -n 20090721mao -s /var/tmp/10_Recom
            2867  /usr/sbin/patchadd -R /a -M /var/tmp/10_Recommended 118666-20 118
              2871  /bin/ksh -hp /usr/lib/patch/patchadd -R /a -M /var/tmp/10_Recom
                8794  pkgadd -O patchPkgInstall -O nozones -O enable-hollow-package
                  8797  /usr/sadm/install/bin/pkginstall -O patchPkgInstall -S -M -
                    29416 /sbin/sh /a/var/sadm/pkg/SUNWj5dmo/install/postinstall
                      29563 rm -r /a/var/sadm/pkg/SUNWj5dmo/save/SUNWj5dmo

## back to output:


    Patch 118666-20 has been successfully installed.
    See /a/var/sadm/patch/118666-20/log for details

    Patch packages installed:
      SUNWj5cfg
      SUNWj5dev
      SUNWj5dmo
      SUNWj5man
      SUNWj5rt

    Checking installed patches...
    Executing prepatch script...
    Verifying sufficient filesystem capacity (dry run method)...
    Installing patch packages...

    ...
    ...
    Checking installed patches...
    Verifying sufficient filesystem capacity (dry run method)...
    Installing patch packages...

    Patch 141765-01 has been successfully installed.
    See /a/var/sadm/patch/141765-01/log for details

    Patch packages installed:
      SUNWdtrp

    Checking installed patches...
    Verifying sufficient filesystem capacity (dry run method)...
    Installing patch packages...

    Patch 141778-02 has been successfully installed.
    See /a/var/sadm/patch/141778-02/log for details

    Patch packages installed:
      SUNWcakr
      SUNWkvm
      SUNWldomr
      SUNWldomu

    Unmounting the BE <20090721mao>.
    The patch add to the BE <20090721mao> failed (with result code <1>). <--------- ??????????

## Everything looks fine, no idea what generated the failure message
## Mike C thinks that the patches against uninstalled packages, etc. would generate a return code sufficient to 
## result in the overall 'error' warning.

## TODO:   validate this by patching with a single 'good' patch, then with a unneeded patch, and compare
## luupgrade exit values.
    -bash-3.00# lustatus 
    Boot Environment           Is       Active Active    Can    Copy      
    Name                       Complete Now    On Reboot Delete Status    
    -------------------------- -------- ------ --------- ------ ----------
    zfsroot                    yes      yes    yes       no     -         
    20090721mao                yes      no     no        yes    -         


## Find the file changes since LU creation (the patch activity)
    -bash-3.00# lucompare -o /var/tmp/20090721mao_patch_changes 20090721mao
    Determining the configuration of 20090721mao ...



    Processing Global Zone
    Comparing / ...

    Compare complete for /.
    Comparing /var ...


    Compare complete for /var.

## The ouput file contains all of the changes, including the changetype:

    for example:
     Sizes differ                                                                                   
     01 < /usr/postgres/8.3/doc/html/functions-admin.html:root:bin:1:33060:REGFIL:27559:
     02 > /usr/postgres/8.3/doc/html/functions-admin.html:root:bin:1:33060:REGFIL:27573:


     Checksums differ                                                                        
     01 < /usr/postgres/8.3/doc/html/view-pg-timezone-abbrevs.html:root:bin:1:33060:REGFIL:3617:534836224:
     02 > /usr/postgres/8.3/doc/html/view-pg-timezone-abbrevs.html:root:bin:1:33060:REGFIL:3617:2668812025:


     Symbolic links are to different files
     Symbolic links are to different files
     01 < /usr/java:root:other:1:41471:SYMLINK:15:
     02 > /usr/java:root:other:1:41471:SYMLINK:15:


    etc.


## Now that we have patched, let's test mounting the alt BE file system to the live BE, and update a file:

## from lumount man page:
     The lumount and luumount commands enable  you  to  mount  or
     unmount  all of the file systems in a boot environment (BE).
     This allows you to inspect or modify the files in a BE while
     that  BE  is not active. By default, lumount mounts the file
     systems on a mount point of the  form  /.alt.BE_name,  where
     BE_name  is  the name of the BE whose file systems are being
     mounted. See NOTES.

## So, run it w/o options (except the BE name), and let it do it's thing
    -bash-3.00# sudo lumount 20090721mao
    /.alt.20090721mao

    # it very kindly returns the mount point.  =]

    ## df:
                           134G   2.4G   109G     3%    /.alt.20090721mao
    /export                109G    20K   109G     1%    /.alt.20090721mao/export
    /export/home           109G    18K   109G     1%    /.alt.20090721mao/export/home
    /rootpool              109G    94K   109G     1%    /.alt.20090721mao/rootpool
    rootpool/ROOT/20090721mao/var
                           134G   4.4G   109G     4%    /.alt.20090721mao/var
    swap                    12G     0K    12G     0%    /.alt.20090721mao/var/run
    swap                    12G     0K    12G     0%    /.alt.20090721mao/tmp


## mod a file:
    -bash-3.00# cd /.alt.20090721mao/etc

    -bash-3.00# cat /.alt.20090721mao/etc/motd 
    Sun Microsystems Inc.   SunOS 5.10      Generic January 2005
    # mike o rules!                             <---------------   this is not from standard jumpstart  =]


## now that we have manipulated the BE, unmount it:

    -bash-3.00# luumount 20090721mao

## Activate the alternate boot environment to be active next reboot:

    ## From luactivate man page:
     The luactivate command, with no arguments, displays the name
     of  the  boot  environment (BE) that will be active upon the
     next reboot of the system. When an argument (a BE) is speci-
     fied, luactivate activates the specified BE.

    -bash-3.00# lustatus    
    Boot Environment           Is       Active Active    Can    Copy      
    Name                       Complete Now    On Reboot Delete Status    
    -------------------------- -------- ------ --------- ------ ----------
    zfsroot                    yes      yes    yes       no     -         
    20090721mao                yes      no     no        yes    -         

    -bash-3.00# luactivate
    zfsroot

    -bash-3.00# luactivate 20090721mao
    A Live Upgrade Sync operation will be performed on startup of boot environment <20090721mao>.


    **********************************************************************

    The target boot environment has been activated. It will be used when you 
    reboot. NOTE: You MUST NOT USE the reboot, halt, or uadmin commands. You 
    MUST USE either the init or the shutdown command when you reboot. If you 
    do not use either init or shutdown, the system will not boot using the 
    target BE.

    **********************************************************************

    In case of a failure while booting to the target BE, the following process 
    needs to be followed to fallback to the currently working boot environment:

    1. Enter the PROM monitor (ok prompt).

    2. Boot the machine to Single User mode using a different boot device 
    (like the Solaris Install CD or Network). Examples:

         At the PROM monitor (ok prompt):
         For boot to Solaris CD:  boot cdrom -s
         For boot to network:     boot net -s

    3. Mount the Current boot environment root slice to some directory (like 
    /mnt). You can use the following command to mount:

         mount -Fzfs /dev/dsk/c1t0d0s0 /mnt

    4. Run <luactivate> utility with out any arguments from the current boot 
    environment root slice, as shown below:

         /mnt/sbin/luactivate

    5. luactivate, activates the previous working boot environment and 
    indicates the result.

    6. Exit Single User mode and reboot the machine.

    **********************************************************************

    Modifying boot archive service

    Activation of boot environment <20090721mao> successful.




    ## status:
    -bash-3.00# lustatus
    Boot Environment           Is       Active Active    Can    Copy      
    Name                       Complete Now    On Reboot Delete Status    
    -------------------------- -------- ------ --------- ------ ----------
    zfsroot                    yes      yes    no        no     -         
    20090721mao                yes      no     yes       no     -         
    -bash-3.00# luactivate
    20090721mao


## Now, reboot.    Wait wait - init or shutdown...    =]

    -bash-3.00# who am i 
    root       console      Jul 15 12:37
    -bash-3.00# hostname
    pststapp01
    -bash-3.00# shutdown -i6 -g0 -y

    ...
    SPARC Enterprise T5220, No Keyboard
    Copyright 2009 Sun Microsystems, Inc.  All rights reserved.
    OpenBoot 4.30.2.b, 32640 MB memory available, Serial #85380300.
    Ethernet address 0:21:28:16:cc:cc, Host ID: 8516cccc.



    Boot device: /pci@0/pci@0/pci@2/scsi@0/disk@0,0:a  File and args: 
    SunOS Release 5.10 Version Generic_141414-02 64-bit
    Copyright 1983-2009 Sun Microsystems, Inc.  All rights reserved.
    Use is subject to license terms.

    ...



    Configuring devices.
    Loading smf(5) service descriptions: 12/12
    Reading ZFS config: done.
    Mounting ZFS filesystems: (8/8)
    pststapp01 console login: 


    [08:47:19 slurm] ~ $ ssh 10.200.19.100 -l root
    Last login: Tue Jul 21 10:42:56 2009 from slurm.thechildr
    Sun Microsystems Inc.   SunOS 5.10      Generic January 2005
    # mike o rules!                       <--------------------------    file modification from inactive BE, now applied.


    -bash-3.00# lustatus
    Boot Environment           Is       Active Active    Can    Copy      
    Name                       Complete Now    On Reboot Delete Status    
    -------------------------- -------- ------ --------- ------ ----------
    zfsroot                    yes      no     no        yes    -         
    20090721mao                yes      yes    yes       no     -         
    -bash-3.00# luactivate
    20090721mao

    ## patch levels:
    ## (just  checking a couple of random levels from those that would have been applied):

    -bash-3.00# showrev -p |grep 'Patch: 139608'  
    Patch: 139608-02 Obsoletes: 120220-01, 120222-31, 125740-01, 136786-01 Requires:  Incompatibles:  Packages: SUNWemlxu, SUNWemlxs
    Patch: 139608-04 Obsoletes: 120220-01, 120222-31, 125740-01, 136786-01 Requires:  Incompatibles:  Packages: SUNWemlxu, SUNWemlxs

    -bash-3.00# uname -a 
    SunOS pststapp01 5.10 Generic_141414-02 sun4v sparc SUNW,SPARC-Enterprise-T5220
    -bash-3.00# cat /etc/release 
                       Solaris 10 5/09 s10s_u7wos_08 SPARC
           Copyright 2009 Sun Microsystems, Inc.  All Rights Reserved.
                        Use is subject to license terms.
                             Assembled 30 March 2009

    ##
    ## Here's the zfs list output, with observations:
    
    
    -bash-3.00# zfs list
    NAME                                        USED  AVAIL  REFER  MOUNTPOINT
    rootpool                                   25.3G   109G    94K  /rootpool
    rootpool/ROOT                              17.3G   109G    18K  legacy
    rootpool/ROOT/20090721mao                  7.25G   109G  2.19G  /
    rootpool/ROOT/20090721mao@20090714a        38.5K      -  2.43G  -       <----- these snapshots were all from the orig BE
    rootpool/ROOT/20090721mao@20090714b          38K      -  2.43G  -       <---   ...
    rootpool/ROOT/20090721mao@20090721mao      4.69M      -  2.43G  -       <---   ...
    rootpool/ROOT/20090721mao/var              4.44G   109G  4.39G  /var
    rootpool/ROOT/20090721mao/var@20090714b    10.4M      -   283M  -       <---   ...
    rootpool/ROOT/20090721mao/var@20090721mao  29.7M      -  4.06G  -       <---   ...
    rootpool/ROOT/zfsroot                      10.0G   119G  2.43G  /       <------ original BE
    rootpool/ROOT/zfsroot/var                  33.6M  9.97G  4.07G  /var    <------ original BE
    rootpool/dump                              4.00G   109G  4.00G  -
    rootpool/export                              38K   109G    20K  /export
    rootpool/export/home                         18K   109G    18K  /export/home
    rootpool/swap                                 4G   113G    16K  -
     
        
        
    ## Everything looks good.

    ## Now, testing the new PROM boot -Z option to test boot from BE choice menu:

    ## The lucreate command added the new BE to the menu.1st file automagically:

    -bash-3.00# pwd
    /rootpool/boot

    -bash-3.00# cat  menu.lst 
    title zfsroot
    bootfs rootpool/ROOT/zfsroot
    title 20090721mao
    bootfs rootpool/ROOT/20090721mao

    ## so, shut it down to ok prompt ( *not* changing the BE with luactivate) :
    -bash-3.00# who am i ; hostname
    root       console      Jul 22 09:02
    pststapp01

    -bash-3.00# shutdown -i 0 -g0 -y

    ## 
    
    SPARC Enterprise T5220, No Keyboard
    Copyright 2009 Sun Microsystems, Inc.  All rights reserved.
    OpenBoot 4.30.2.b, 32640 MB memory available, Serial #85380300.
    Ethernet address 0:21:28:16:cc:cc, Host ID: 8516cccc.



    {0} ok boot -L
    Boot device: /pci@0/pci@0/pci@2/scsi@0/disk@0,0:a  File and args: -L
    1 zfsroot
    2 20090721mao
    Select environment to boot: [ 1 - 2 ]: 1

    To boot the selected entry, invoke:
    boot [<root-device>] -Z rootpool/ROOT/zfsroot

    Program terminated
    {0} ok boot  -Z rootpool/ROOT/zfsroot

    
    Boot device: /pci@0/pci@0/pci@2/scsi@0/disk@0,0:a  File and args: -Z rootpool/ROOT/zfsroot
    krtld: Ignoring invalid kernel option -Z.
    krtld: Unused kernel arguments: `rootpool/ROOT/zfsroot'.

    # From:
    # http://www.solarisinternals.com/wiki/index.php/ZFS_Troubleshooting_Guide
        "   
         ZFS Boot Error Messages

            * CR 2164779 - Ignore the following krtld messages from the boot -Z command. They are harmless: 

          krtld: Ignoring invalid kernel option -Z.
          krtld: Unused kernel arguments: `rpool/ROOT/zfs1008BE'.

        "
    -bash-3.00# luactivate
    zfsroot
    -bash-3.00# lustatus
    Boot Environment           Is       Active Active    Can    Copy      
    Name                       Complete Now    On Reboot Delete Status    
    -------------------------- -------- ------ --------- ------ ----------
    zfsroot                    yes      yes    yes       no     -         
    20090721mao                yes      no     no        yes    -   

    ## And, obviously back in the original BE:

    # back to the boring default.
    -bash-3.00# cat /etc/motd
    Sun Microsystems Inc.   SunOS 5.10      Generic January 2005

    # 20090721mao patched BE is Generic_141414-02
    -bash-3.00# uname -a
    SunOS pststapp01 5.10 Generic_139555-08 sun4v sparc SUNW,SPARC-Enterprise-T5220   

    # 20090721mao patched BE was 139608-04
    -bash-3.00# showrev -p |grep 'Patch: 139608'
    Patch: 139608-02 Obsoletes: 120220-01, 120222-31, 125740-01, 136786-01 Requires:  Incompatibles:  Packages: SUNWemlxu, SUNWemlxs

    NAME                                        USED  AVAIL  REFER  MOUNTPOINT
    rootpool                                   25.3G   109G    94K  /rootpool
    rootpool/ROOT                              17.3G   109G    18K  legacy
    rootpool/ROOT/20090721mao                  7.25G   109G  2.19G  /
    rootpool/ROOT/20090721mao@20090714a        38.5K      -  2.43G  -
    rootpool/ROOT/20090721mao@20090714b          38K      -  2.43G  -
    rootpool/ROOT/20090721mao@20090721mao      4.69M      -  2.43G  -
    rootpool/ROOT/20090721mao/var              4.44G   109G  4.39G  /var
    rootpool/ROOT/20090721mao/var@20090714b    10.4M      -   283M  -
    rootpool/ROOT/20090721mao/var@20090721mao  29.7M      -  4.06G  -
    rootpool/ROOT/zfsroot                      10.0G   119G  2.43G  /
    rootpool/ROOT/zfsroot/var                  33.9M  9.97G  4.07G  /var
    rootpool/dump                              4.00G   109G  4.00G  -
    rootpool/export                              38K   109G    20K  /export
    rootpool/export/home                         18K   109G    18K  /export/home
    rootpool/swap                                 4G   113G    16K  -


```

#ZFS Adding Swap device
```bash
[13:10:52 dbtst01] ~ $ sudo zfs create -b 8192 -V 4096m rootpool/swap1     

[13:11:10 dbtst01] ~ $ sudo swap -a /dev/zvol/dsk/rootpool/swap1
```

#ZFS Boot into Single User
```bash


SINGLE USER MODE

# zpool list
no pools available
# zfs list
no datasets available

# zpool import -R /mnt -a

# zfs list -t filesystem
NAME                          USED  AVAIL  REFER  MOUNTPOINT
rootpool                     15.0G   119G    94K  /mnt/rootpool
rootpool/ROOT                6.93G   119G    18K  legacy
rootpool/ROOT/initialBE      6.93G   119G  3.71G  /mnt
rootpool/ROOT/initialBE/var  2.91G  12.1G  2.86G  /mnt/var
rootpool/export               722K  10.0G    20K  /mnt/export
rootpool/export/home          670K  10.0G   233K  /mnt/export/home




## now that we have the zpool imported, we can mount the ZFS filesystems that we need:

# zfs mount rootpool/ROOT/initialBE

# ls -la /mnt
total 140
drwxr-xr-x  27 root     root          32 Nov 13 12:34 .
drwxr-xr-x  19 root     root         512 Mar 30  2009 ..
drwxr-xr-x   2 root     sys            2 Oct 24 16:23 .@localstatedirroot@
drwxr-xr-x   2 root     sys            2 Oct 24 16:23 .@sysconfdirroot@
-rw-------   1 root     root          24 Oct 25 16:19 .bash_history
-rw-r--r--   1 root     root          40 Aug 19 09:54 .forward
-rwxr--r--   1 root     root          46 Nov  4 12:26 .osuuid
drwx------   2 root     root           3 Oct 24 16:01 .ssh
drwx------   3 root     root           3 Oct 24 16:23 .sunw
lrwxrwxrwx   1 root     root           9 Oct 24 15:54 bin -> ./usr/bin
drwxr-xr-x   3 root     sys            3 Oct 24 15:55 boot
drwxr-xr-x  21 root     sys          294 Nov 13 12:15 dev
drwxr-xr-x  12 root     sys           12 Nov 17 08:24 devices
drwxr-xr-x  69 root     sys          225 Nov 13 12:34 etc
drwxr-xr-x   2 root     root           2 Nov  5 14:32 export
dr-xr-xr-x   2 root     root           2 Oct 24 15:56 home
drwxr-xr-x  15 root     sys           15 Oct 24 15:57 kernel
drwxr-xr-x   7 root     bin          243 Oct 24 15:58 lib
drwxr-xr-x   2 root     sys            2 Oct 24 15:54 mnt
dr-xr-xr-x   2 root     root           2 Oct 24 16:23 net
-rw-r--r--   1 root     root           0 Oct 24 16:01 noautoshutdown
drwxr-xr-x  36 root     sys           36 Nov 13 08:11 opt
drwxr-xr-x  40 root     sys           47 Oct 24 15:55 platform
dr-xr-xr-x   2 root     root           2 Oct 24 15:54 proc
drwxr-xr-x   2 root     root           2 Oct 24 15:54 rootpool
drwxr-xr-x   2 root     sys           66 Nov  4 12:49 sbin
drwxr-xr-x   4 root     root           4 Oct 24 15:54 system
drwxr-xr-x  10 root     root          10 Nov  5 13:21 tch
drwxrwxrwt   2 root     sys            2 Nov 17 08:25 tmp
drwxr-xr-x  35 root     sys           49 Nov 13 08:11 usr
drwxr-xr-x   2 root     root           2 Oct 24 15:54 var
drwxr-xr-x   2 root     root           2 Oct 24 16:23 vol


## Now in this case, we wish to revert to pre- 'stsmboot -e' modifications.

## so, I exported my TERM to xterms, and edited /mnt/kernel/drv/fp.conf, removing the 
## damage done by the stmsboot cmd - 

from:
disable-sata-mpxio="no";

to:
#disable-sata-mpxio="no";

and rebooted.
```

