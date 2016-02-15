Title: Setting up a pelican blog
Date: 
Modified: 2016-02-12 10:20
Category: Blog
Tags: pelican, publishing, blog
Slug: setting-up-a-pelican-blog
Authors: Craig Riley
Summary: Experimenting with Pelican

So here is something. Why ever bother with a static webpage generator when you can easily setup a powerful web framework like Django or Wordpress or Drupal?

All wonderful questions. I dont really know.

One reason might be that security is in order. The thoguht that your exposure to the intnernet is static. There are no database hooks to take advanatage of, no php vulnerabilities, no dynamic rendering that you need to be concerned with. What ever is rendered is what ever is rendered and that is what you get.

CSS and JS run on the client machine and as such can't be exploited on the server because there is nothing to exploit.

Kind of cool.

The other thing that is kind of cool with this whole pelican thing is how simple it is. You edit your file in an ediotor ( I use VIM because I've been using it for years and years and the key bindings are engraned at this point) and then you just save the file and the geneartor creates the output.

Markdown isn't too difficult to use either. Although out of the box there are definately some things to tweak. For exmaple: Its pretty plain looking!

So here are the basic steps to setup Pelican. 

1. Configure your environment
2. Add a theme
3. Create Some Content


## Configure your environment

First we need to install the software - this could not be simplier. 

```bash
$ pkg install  virtualenv

# now lets enable the virtualenv
# i happened to name my virtualenv "pelican"

$ virtualenv pelican
$ cd pelican/
$ . bin/activate
$ pip install pelican markdown
$ pelican-quickstart 

```
you will be asked a bunch of setup questions about your site. You can update these parameters in your pelicanconf.py file after the fact if you want to change something. 

Lets start the development server
```bash

$ ./develop_server.sh start
```
Now lets download a theme - this one works ok but you'll want to tweak it.
```bash
$ git clone https://github.com/DandyDev/pelican-bootstrap3.git
```

## Lets point pelican to our new theme

Now that we have Pelican installed and running and we've downloaded our theme files we need to tell Pelican where to find the theme.  This I find very elegant, there are many frameworks that make theme installation easy but I think this takes the cake. 

Open up the pelicanconf.py file and add the following:

```python
THEME = 'pelican-bootstrap3'
```

## Create some content:

```markdown

Title: Setting up a pelican blog
Date: 2016-02-12 10:20
Modified: 2016-02-12 10:20
Category: Blog
Tags: pelican, publishing, blog
Slug: setting-up-a-pelican-blog
Authors: Craig Riley
Summary: Experimenting with Pelican

Create your content using the editor of your choice. 

> This is a block quote!


```

That is pretty much it! You have a blog that you can write and add content to without too much trouble.  

Once you get the hang of the whole markdown thing *which I am still working on ;-) * then you can make it look better. 

# Lets add some color to the theme!

So this i think is pretty cool.  You will edit the rendered css in the output direcotry and NOT the actual theme you downloaded using GIT. 

Why is that important? Well, out of the box we can modify the theme to be like we want it without having to change the actual code. If updates come about we can apply them without jacking everythign up. 

We can easily change the applied background color of the site by adding a background css tag to the style.css

```css
body {
    padding-top: 70px;
    background:#b3ecff;
}
.navbar {
        background:#f0f5f5;

}
```

# And maybe some images???

![This is the alternate text](/images/pelican.jpg) This would be a snazzy example of inserting an image inline with very little code. 

```markdown
![This is the alternate text](/images/pelican.jpg) This would be a snazzy example of inserting an image inline with very little code. 


```
