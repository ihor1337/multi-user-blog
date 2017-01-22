# Multi User Blog
Multiuser blog is a blog website built using the Google App Engine
Framework

The website is accessible by this link: https://chrome-bearing-151421.appspot.com/

#### Note:
This website uses flexbox layout. Please make sure that you use [latest](http://browsehappy.com/) version of your browser.
IE below 11 is not supported (IE 11 supported partially, see http://caniuse.com/#search=flexbox)

### How to run it locally:
- Install Python Google Cloud SDK for your operating system.
(Refer the official [documentation](https://cloud.google.com/appengine/docs/python/download)
for more details)
- Clone or download this repo
- Navigate to the root directory of the project
- Open the terminal (within the root directory)
and run this command
```sh
dev_appserver.py app.yaml
```
- Navigate to http://localhost:8080 in your browser
- You can also specify the port if required by adding flag ```--port=3000```
so the command should look like
```sh
dev_appserver.py --port=3000 app.yaml
```

### References:
- [StackOverflow](stackoverflow.com) forums
- [Udacity](https://discussions.udacity.com/c/nd004-p2-multi-user-blog) forums
