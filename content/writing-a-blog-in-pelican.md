Title: Writing a Blog with a Static Web Page Generator
Date: 2016-02-12 10:20
Modified: 2016-02-12 10:20
Category: Blog
Tags: pelican, publishing, blog
Slug: writing-a-blog-with-a-static-web-page-generator
Authors: Craig Riley
Summary: Trying out a static webpage generator

So here is something. Why ever bother with a static webpage generator when you can easily setup a powerful web framework like Django or Wordpress or Drupal?

All wonderful questions. I dont really know. 

One reason might be that security is in order. The thoguht that your exposure to the intnernet is static. There are no database hooks to take advanatage of, no php vulnerabilities, no dynamic rendering that you need to be concerned with.  What ever is rendered is what ever is rendered and that is what you get. 

CSS and JS run on the client machine and as such can't be exploited on the server because there is nothing to exploit. 

Kind of cool. 


The other thing that is kind of cool with this whole pelican thing is how simple it is. You edit your file in an ediotor ( I use VIM because I've been using it for years and years and the key bindings are engraned at this point) and then you just save the file and the geneartor creates the output. 

Markdown isn't too difficult to use either. Although out of the box there are definately some things to tweak.  For exmaple: Its pretty plain looking! 

```python

s = "Python syntax highlighting"
print s
```

#And here is a heading 
#
#
> and this is a block quote. 
#
Tables might work like this:

Column 1 | Column 2 | Column 3
--- | --- | ---
*One* | `renders` | **nicely**

