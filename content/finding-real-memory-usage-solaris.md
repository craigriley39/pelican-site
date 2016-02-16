Title: Notes - Finding Real Memory Usage - Solaris
Date: 2016-02-15 10:20
Modified: 2016-02-15 10:20
Category: Unix
Tags: solaris
Authors: Craig Riley
Summary: Finding the real memory in use on Solaris 10
# Finding the real memory in use
```bash


[10:30:35 pststapp03] ~ $ sudo mdb -k
Loading modules: [ unix krtld genunix specfs dtrace ufs sd px ssd fcp fctl md qlc ip hook neti sctp arp usba lofs zfs random nfs crypto ipc ptm logindmux cpc fcip ]
> ::memstat

Page Summary                Pages                MB  %Tot
------------     ----------------  ----------------  ----
Kernel                     133624              1043    3%     <------OS and others (vxfs cache)
Anon                        57146               446    1%
Exec and libs               22366               174    1%
Page cache                 359381              2807    9%     <------UFS cache stuff
Free (cachelist)           733145              5727   18%
Free (freelist)           2865356             22385   69%

Total                     4171018             32586
Physical                  4104612             32067


[10:29:01 pststapp03] ~ $ vmstat 1
 kthr      memory            page            disk          faults      cpu
 r b w   swap  free  re  mf pi po fr de sr m1 m1 m1 m2   in   sy   cs us sy id
 0 0 0 41581664 31079760 242 191 13 6 4 0 1 2  2  2  2  793 3212  892  1  0 99
 0 0 0 41385720 28277640 11 19 0 0 0  0  0  0  0  0  0  545  652  551  0  0 100
 0 0 0 41385528 28277536 0 1 0  0  0  0  0  0  0  0  0  535  512  521  0  0 99
 0 0 0 41385528 28277536 0 0 0  0  0  0  0  0  0  0  0  568  491  578  0  1 99
 0 0 0 41385528 28277536 0 0 0  0  0  0  0  0  0  0  0  531  552  553  0  1 99
 0 0 0 41385528 28277536 0 1 0  0  0  0  0  0  0  0  6  599 1660  601  0  1 99


[10:37:23 pststapp03] ~ $ echo 'scale=2; 28277072/1024/1024' |bc
26.96
```
