import os
import web
from jinja2 import Environment, FileSystemLoader
from passlib.hash import pbkdf2_sha256 as sha256
# Sessions don't work in debug mode.
web.config.debug = False

##########################################################################
################# DO NOT CHANGE ANYTHING ABOVE THIS LINE! ################
##########################################################################

# If you need custom modules, uncomment the following line, create a 
# lib directory under your wsgi directory, and place your modules there.
# Make sure that file/directory permissions are set appropriately.
#
#import sys; sys.path.insert(0, 'lib')

###################### BEGIN HELPER METHODS ######################

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),
                                             'templates')),
                                extensions=extensions)
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)
    web.header('Cache-Control',
               'no-cache, max-age=0, must-revalidate, no-store',
               unique=True
    )

    return jinja_env.get_template(template_name).render(context)

##################### END HELPER METHODS #####################

# URL to class mappings.
urls = (
    '/', 'login',
    '/login', 'login',
    '/logout', 'logout',
    '/welcome','welcome', 
    '/create','create',
    '/bluecheese','search',
    '/search','search',
    '/trip','trip',
    '/Tsearch','Tsearch',
    '/addbike','addbike'
	'/becomeowner','becomowner'
)

# Create the database object.
db = web.database(dbn='postgres', user='guigriffins', pw='guigriffins',
                  db='guigriffins')

# Create the application object.
app = web.application(urls, globals())

# Create the session object, initializing it (first use) or restoring it
# (subsequent uses), as necessary.
# Use the initializer dictionary to
# declare and initialize your session variables.
# WARNING: DO NOT CHANGE web.session.DiskStore()'S PARAMETER!
session = web.session.Session(app,
          web.session.DiskStore('/var/lib/php/session'),
              initializer={'loggedIn': False, 'user' : '', 'name' : 'default name'}
   )

class login:
    def GET(self):
        if session.loggedIn:
            raise web.seeother('/welcome')
        else:
            return render_template('Login.html')

    def POST(self):
        email, passwd = web.input().email, web.input().passwd
        try:
            # Prevent SQL injection attacks.
	    query = 'select * from person where email=$eml;'
            vars = {'eml':email}
            result = db.query(query, vars)[0]
	    print(result)
	    print(result['password'])
	    print(result['userid'])
	
            if sha256.verify(passwd,result['password']):
               session.loggedIn = True
               session.user = result['userid']
	       session.name = result['firstname']
               return render_template('welcome.html', name = session.name)
	except:
            pass
        raise web.seeother('/')

class welcome:
    def GET(self):
        if session.loggedIn:
	    query= 'select count(1) from owner where userid = $usrid;'
	    vars= {'usrid':session.user}
	    count = db.query(query,vars)[0]
	    return render_template('welcome.html', name = session.name, count = count['count'], user = session.user)
        else:
            raise web.seeother('/')

class logout:
    def GET(self):
        session.loggedIn = False
        session.kill()
       # return render_template('Logout.html')
	raise web.seeother('/')
class create:
    def GET(self):
	return render_template('createAccount.html')

    def POST(self):
	try:
	    hashedPswd = sha256.hash(web.input().passwrd)
	    db.insert('person', email = web.input().email, firstname = web.input().fName, lastname = web.input().lName,phonenumber = web.input().phNum, password = hashedPswd)	
	    raise web.seeother('/login')
	except:
		pass

class search:
    def GET(self):
	allZips = list(db.query('select * from uniqZIPs;'))
	return render_template('bikeSearch.html',name = session.name, allzips = allZips)
		
    def POST(self):
	zipCode = web.input().zip
	query = 'select * from bike where ZIPCode = $zip;'
	vars = {'zip':zipCode}
	results = list(db.query(query,vars))
		
	return render_template('bikeResult.html',name = session.name, results = results)		

class trip:
	
    def POST(self):
	#Get bike information
	bikeID = web.input().bikeId
	print(bikeID)
	query = 'select * from bike where bikeid = $bID'
	vars = {'bID':bikeID}
	bike = db.query(query,vars)[0]
	print(bike)
	print(bike['ownerid'])
	
	#Get owner information
        query = 'select userid,firstname,rating from person natural join (select * from owner where userID = $ownrID) as t1;'
        vars = {'ownrID': bike['ownerid']}
        print(db.query(query,vars))
	owner = db.query(query,vars)[0]
	
	#Render page
        return render_template('bookTrip.html', bike = bike, owner = owner)
        
            
class Tsearch:
	
	def POST(self):
		#get trip info for owners
		myTrip = list(db.query('select * from trips where OwnerID = session.user;'))
		return render_template('reviewTest.html',name=session.name, aTrip=myTrip)
    
    
    

#class book:
 #   def POST(self):
#	hrlyOrDly = web.input().hrlyOrDly
#	tripLength = web.input().length
#	startDate = 
#	startTime = 



class becomeover :
	 def GET(self):
		return render_template('becomeowner.html')
	
	#def POST(self):
	#banknumber = web.input().banknumber
	
	
##########################################################################
################# DO NOT CHANGE ANYTHING BELOW THIS LINE! ################
##########################################################################
#
# Boilerplate code to run the app on either the development server or
# the production server (Apache).  To run on the development server:
#
#    python dbdemo.py [ port ]
#
# where the optional port argument is used to specify a port, other
# then the default 8080, for the server to listen on.  The port number
# must be unused and in the range [1024, 65535].


if __name__ == "__main__":
    # Run on development server.
    app.run()
else:
    # Run on apache.
    application = app.wsgifunc()
