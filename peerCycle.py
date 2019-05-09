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
    '/addbike','addbike',
    '/book','book',
    '/becomeowner','becomeowner',
    '/becomerenter','becomerenter',
    '/Tsearch','Tsearch',
    '/review', 'review'
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
	    try:
		#Check if user is in owner table
    	        query= 'select count(1) from owner where userid = $usrid;'
	        vars= {'usrid':session.user}
	        isOwner = db.query(query,vars)[0]
		#Check if user is in renter table
		query = 'select count(1) from renter where userid = $usrid;'
		isRenter = db.query(query,vars)[0]
		
	        return render_template('welcome.html', name = session.name, isOwner = isOwner['count'],isRenter = isRenter['count'], user = session.user)
            except:
	       return render_template('welcome.html',name = session.name, count = 0)
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
	def GET(self):
		#get trip info for owners and riders
		Trip = 'select * from trips where renterid = $usrid;'
		Otrip = 'select * from trips where ownerid = $usrid;'
		vars = {'usrid':session.user}
		Trips = list(db.query(Trip,vars))
		Otrips = list(db.query(Otrip,vars))
			
		return render_template('searchTrips.html', rentResults = Trips, ownResults = Otrip, name = session.name, us = session.user)

class review:
	def GET(self):
		trip = web.input().tripid
		print(trip)
		return render_template('review.html', trip = trip)
	
	def POST(self):
		trid = web.input().trip
		star = web.input().rating
		comment = web.input().message
		vars = {'tar':trid}
		rid = db.query('select renterid from trips where tripid = $tar', vars)
		#oid = db.query('select ownerid from trips where tripid = $tar',vars)
		db.insert('reviews', tripid = trid, reviewerid = session.user ,review = star ,comments = comment)
		vars = {'s':star, 'st':trid}
		if (rid == session.user):
			db.query('update trips set riderexperience = $s where tripid = $st;',vars)
		else:
			db.query('update trips set ownerexperience = $s where tripid = $st;',vars)
		return render_template('reviewSent.html')
				       
class book:
    def POST(self):

# Define variables
	hrlyOrDly = web.input().hrlyOrDly
	tripLength = web.input().length
	startDate = web.input().startDate 
	startTime = web.input().startTime
	bikeid = web.input().bikeId
	tip = web.input().tip
	tip = float(tip[1:])
	isHrly = None	
	price = None
	ownerid = None
        vars = {'bkid':bikeid}
	
# Check to see if trip is by the hour or day       
        if hrlyOrDly == "hrly":
	    isHrly = True
    	    query = 'select hlyRate,ownerid from bike where bikeid = $bkid' 
	    result = db.query(query,vars)[0]
	   # return result
  	    price = result['hlyrate']
	    ownerid = result['ownerid']
	else:
	    isHrly = False
	    query = 'select dlyRate,ownerid from bike where bikeid = $bkid'
	    result = db.query(query,vars)[0]
            price = result['dlyrate']
	    ownerid = result['ownerid']

# Compute the costs associated with the trip
	derivedCost = float(tripLength)*float(price)
	tax = derivedCost*0.06
	totalCost = derivedCost + tax + tip

# Format Timestamp
	timeStamp = startDate + " " + startTime

#Insert into DB	
	db.insert('trips', isHrly = isHrly, NumOfHrsDays = tripLength, StartTime = timeStamp, Tip = tip, Tax = tax, DerivedCost = derivedCost, TotalCost = totalCost, OwnerId = ownerid, RenterId = session.user) 	

# Select created Trip to use for reciept page/make sure inserted properly into DB
        query = 'select * from trips where ownerid = $ownerid and renterid = $usrid and StartTime = $starttime'	
	vars = {'ownerid':ownerid,'usrid' : session.user,'starttime': timeStamp}
	trip = db.query(query,vars)[0]
	return render_template('tripReceipt.html',trip=trip) 
	
	



class becomeowner :
#	 def GET(self):
#		return render_template('becomeOwner.html')
	
	 def POST(self):
	     banknumber = web.input().BankNo
	     query = 'insert into owner values ($usrid, Null,$bankno);'
	     vars = {'usrid':session.user,'bankno':banknumber}
	     raise web.seeother('/welcome')

class becomerenter:
	def POST(self):
	    creditnumber = web.input().CreditNo
	    query = 'insert into renter values ($usrid,Null,$creditno);'
	    vars = {'usrid':session.user,'creditno':creditnumber}
	    db.query(query,vars)
	    raise web.seeother('/welcome')
	 
class addbike:
    def GET(self):
	allZips = list(db.query('select * from uniqzips'))
	return render_template('addbike.html',allzips = allZips) 

    def POST(self):
#Get user input
	make = web.input().Make
	model = web.input().Model
	year = web.input().ModelYear
	description = web.input().message
	dlyrate = web.input().dlyrate
	hlyrate = web.input().dlyrate
	biketype = web.input().biketype
	street = web.input().streetaddress
	city = web.input().city
	state = web.input().state
	zipcode = web.input().zipcode
	lockcode = web.input().lockcode
#Insert into db
	vars = {'ownerid':session.user,'make':make,'model':model,'tstamp': "01 01 " + year,'desc':description,
'dlyrate':dlyrate,'hlyrate':hlyrate,'biketype':biketype,'address':street,'city':city,'state':state,'zip':zipcode, 'lockcode':lockcode}

	query = 'insert into bike values(default,$ownerid,$address,$city,$state,$zip,$dlyrate,$hlyrate,$model,$make,$biketype,$tstamp)'
	db.query(query,vars)
	return render_template('ownerbikes.html')
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
