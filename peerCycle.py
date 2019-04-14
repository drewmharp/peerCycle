import os
import web
from jinja2 import Environment, FileSystemLoader

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
    
)

# Create the database object.
db = web.database(dbn='postgres', user='demo', pw='demo',
                  db='registration')

# Create the application object.
app = web.application(urls, globals())

# Create the session object, initializing it (first use) or restoring it
# (subsequent uses), as necessary.
# Use the initializer dictionary to
# declare and initialize your session variables.
# WARNING: DO NOT CHANGE web.session.DiskStore()'S PARAMETER!
session = web.session.Session(app,
          web.session.DiskStore('/var/lib/php/session'),
              initializer={'loggedIn': False, 'user' : ''}
          )

class login:
    def GET(self):
        if session.loggedIn:
            raise web.seeother('/welcome')
        else:
            return render_template('login.html')

    def POST(self):
        user, passwd = web.input().user, web.input().passwd
        try:
            # Prevent SQL injection attacks.
            query = 'select * from users where username=$usr;'
            vars = {'usr':user}
            result = db.query(query, vars)[0]
            if passwd == result['password']:
                session.loggedIn = True
                session.user = user
                return render_template('welcome.html', user=session.user)
        except:
            pass
        raise web.seeother('/')

class welcome:
    def GET(self):
        if session.loggedIn:
            return render_template('welcome.html', user=session.user)
        else:
            raise web.seeother('/')

class logout:
    def GET(self):
        session.loggedIn = False
        session.kill()
        return render_template('logout.html')

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
