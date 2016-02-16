Title: Thoughts on securing a web blog
Date: 2016-02-14 10:20
Modified: 2016-02-14 10:20
Category: Blog
Tags: pelican, security
Authors: Craig Riley
Summary: Thoughts on securing a web blog

#Securing a web blog 


I figure that the more software you have running the more you have to worrry about.  To that end I decided I would take a slightly different approach with the whole blogging thing for that reason and a couple more. 

Here are some things that I considered:

1. Who is going to read the thing?
2. How do you like to write? and do you care about collaboration?
3. What do you really need it to do?

There are other questions but for me those three were the ones that stuck out.  
1. Who is going to read the thing? - A. In all liklihood, me.  There are tons of things and notes and items that I have collected in one form or another that I keep coming back to. Maybe I work on a piece of technology and then dont revisit it for a really long time. All the tips and tricks and things and such that I've picked up leave my head and its good to ahve someplace that I can go to remember. 

2. How do you like to write? and do you care about collaboration? A. For me, I like to write quick and simple notes in Vi. I have been using that editor for many, many years and its just something that I'm very familar with.  And no...I am not interested in collaboarting this is just for me. 

3. What do you really need it to do? A. Well, not much! I really dont need a blog to do much at all. Store pages, Orgnaize things into topics and themes and allow me to search throgh them fairly quickly. That's pretty much it. 

The other thing that I worry about is security. I setup a default wordpress site once and was amazed at how many bogus comments I ended up getting. The longer I leeft the site up with the default config the more I would get. Hundreds of completely bogus comments. I have no idea why.  Now Wordpress does a fairly good job with security but running it in production elsewhere it was clear to see that the more functionality you have the more you have to exploit . Simplier is better if simple is all you need! 

So that's what's up with this project.  I figured I would go with a static blog and if I wnated to do something more elaborate in the future I could move this to github for future refernce.  

So there you have it...a completely static web blog created using pelican. Simple Linux box, Nginx serving a static directory on a local file system and a site created using css/js and html5 templates.  Simple :-)

