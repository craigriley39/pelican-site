Title: Notes - VIM Tricks
Date: 2016-02-15 10:20
Modified: 2016-02-15 10:20
Category: Unix
Tags: vim
Authors: Craig Riley
Summary: Hacks and Tricks for the VIM editor

>swiped from [http://www.zinkwazi.com/unix/notes/tricks.vim.html](http://www.zinkwazi.com/unix/notes/tricks.vim.html)

Where grep came from (RE being Regular Expression):
```bash
:g/RE/p
```
Delete lines 10 to 20 inclusive:
```bash
:10,20d
```
or with marks a and b:
```bash
:'a,'bd
```
Delete lines that contain pattern:
```bash
:g/pattern/d
```
Delete all empty lines:
```bash
:g/^$/d
```
Delete lines in range that contain pattern:
```bash
:20,30/pattern/d
```
or with marks a and b:
```bash
:'a,'b/pattern/d
```
Substitute all lines for first occurance of pattern:
```bash
:%s/pattern/new/
:1,$s/pattern/new/
```
Substitute all lines for pattern globally (more than once on the line):
```bash
:%s/pattern/new/g
:1,$s/pattern/new/g
```
Find all lines containing pattern and then append -new to the end of each line:
```bash
:%s/\(.*pattern.*\)/\1-new/g
```
Substitute range:
```bash
:20,30s/pattern/new/g
```

with marks a and b:
```bash
:'a,'bs/pattern/new/g

```
Swap two patterns on a line:
```bash
:s/\(pattern1\)\(pattern2\)/\2\1/
```
Capitalize the first lowercase character on a line:
```bash
:s/\([a-z]\)/\u\1/
```
more concisely:
```bash
:s/[a-z]/\u&/
```
Capitalize all lowercase characters on a line:
```bash
:s/\([a-z]\)/\u\1/g
```
more concisely:
```bash
:s/[a-z]/\u&/g
```
Capitalize all characters on a line:
```bash
:s/\(.*\)/\U\1\E/
```
Capitalize the first character of all words on a line:
```bash
:s/\<[a-z]/\u&/g
```
Uncapitalize the first character of all words on a line:
```bash
:s/\<[A-Z]/\l&/g
```

Change case of character under cursor:
```bash
~
```
Change case of all characters on line:
```bash
g~~
```
Change case of remaining word from cursor:
```bash
g~w
```

Turn on line numbering:
```bash
:set nu
```
Turn it off:
```bash
:set nonu
```
Number lines (filter the file through a unix command and replace with output):
```bash
:%!cat -n
```

Sort lines:
```bash
:%!sort
```
Sort and uniq:
```bash
:%!sort -u
```
Read output of command into buffer:
```bash
:r !ls -l
```
Refresh file from version on disk:
```bash
:e!
```

Set textwidth for automatic line-wrapping as you type:
```bash
:set textwidth=80
```
Turn on syntax highlighting
```bash
:syn on
```
Turn it off:
```bash
:syn off
```
Force the filetype for syntax highlighting:
```bash
:set filetype=python
:set filetype=c
:set filetype=php
```
Use lighter coloring scheme for a dark background:
```bash
:set background=dark

Htmlize a file using the current syntax highlighting:
```bash
:so $VIMRUNTIME/syntax/2html.vim
```

Or, htmlize from a command prompt:
in 2html.sh put:
```bash
#!/bin/sh
vim -n -c ':so $VIMRUNTIME/syntax/2html.vim' -c ':wqa' $1 > /dev/null 2> /dev/null
```
Now just run:  
```bash
shell> 2html.sh foo.py
```
