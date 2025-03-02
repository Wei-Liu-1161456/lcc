from loginapp import app
from loginapp import db
from flask import redirect, render_template, request, session, url_for, flash
from flask_bcrypt import Bcrypt
import MySQLdb.cursors
import re

# Create an instance of the Bcrypt class, which we'll be using to hash user
# passwords during login and registration.
flask_bcrypt = Bcrypt(app)

# Default role for new users
DEFAULT_USER_ROLE = 'visitor'

# Password validation pattern
# At least 8 characters, must include uppercase, lowercase, and numbers
PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

def user_home_url():
    """Generates a URL to the homepage for the currently logged-in user.
    
    If the user is not logged in, this returns the URL for the login page
    instead. If the user appears to be logged in, but the role stored in their
    session cookie is invalid (i.e. not a recognised role), it returns the URL
    for the logout page to clear that invalid session data."""
    if 'loggedin' in session:
        role = session.get('role', None)
        if role == 'visitor':
            home_endpoint = 'visitor_home'
        elif role == 'helper':
            home_endpoint = 'helper_home'
        elif role == 'admin':
            home_endpoint = 'admin_home'
        else:
            home_endpoint = 'logout'
    else:
        home_endpoint = 'login'
    
    return url_for(home_endpoint)

@app.route('/')
def root():
    """Root endpoint (/)
    
    Methods:
    - get: Redirects guests to the login page, and redirects logged-in users to
        their own role-specific homepage.
    """
    return redirect(user_home_url())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page endpoint.

    Methods:
    - get: Renders the login page.
    - post: Attempts to log the user in using the credentials supplied via the
        login form, and either:
        - Redirects the user to their role-specific homepage (if successful)
        - Renders the login page again with an error message (if unsuccessful).
    
    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """
    if 'loggedin' in session:
         return redirect(user_home_url())

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s AND status = "active"', (username,))
            user = cursor.fetchone()

        if user and flask_bcrypt.check_password_hash(user['password_hash'], password):
            session['loggedin'] = True
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(user_home_url())
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html', username=username, error=True)

    # This was a GET request, or an invalid POST (no username and/or password),
    # so we just render the login form with no pre-populated details or flags.
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup (registration) page endpoint.

    Methods:
    - get: Renders the signup page.
    - post: Attempts to create a new user account using the details supplied
        via the signup form, then renders the signup page again with a welcome
        message (if successful) or one or more error message(s) explaining why
        signup could not be completed.

    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """
    if 'loggedin' in session:
         return redirect(user_home_url())
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        location = request.form['location']

        # Input validation
        errors = {}
        
        # Username validation
        if not username or len(username) > 20:
            errors['username'] = 'Username is required and must be less than 20 characters'
        
        # Email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Please enter a valid email address'

        # Password validation
        if not re.match(PASSWORD_PATTERN, password):
            errors['password'] = 'Password must be at least 8 characters and include uppercase, lowercase, and numbers'

        # Name validation
        if not first_name or len(first_name) > 50:
            errors['first_name'] = 'First name is required and must be less than 50 characters'
        if not last_name or len(last_name) > 50:
            errors['last_name'] = 'Last name is required and must be less than 50 characters'
        
        # Location validation
        if not location or len(location) > 50:
            errors['location'] = 'Location is required and must be less than 50 characters'

        if not errors:
            # Check if username already exists
            with db.get_cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
                if cursor.fetchone():
                    errors['username'] = 'Username already exists'
                else:
                    # Create new user
                    hashed_password = flask_bcrypt.generate_password_hash(password)
                    try:
                        cursor.execute(
                            'INSERT INTO users (username, password_hash, email, first_name, last_name, location, role, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                            (username, hashed_password, email, first_name, last_name, location, DEFAULT_USER_ROLE, 'active')
                        )
                        db.get_db().commit()
                        flash('Registration successful! Please log in.', 'success')
                        return redirect(url_for('login'))
                    except Exception as e:
                        errors['database'] = 'An error occurred during registration'

        # If there were errors, re-render the form with error messages
        return render_template('signup.html', errors=errors, 
                             username=username, email=email,
                             first_name=first_name, last_name=last_name,
                             location=location)

    # GET request - show empty form
    return render_template('signup.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """User Profile page endpoint.

    Methods:
    - get: Renders the user profile page for the current user.

    If the user is not logged in, requests will redirect to the login page.
    """
    if 'loggedin' not in session:
         return redirect(url_for('login'))

    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        location = request.form['location']
        
        with db.get_cursor() as cursor:
            cursor.execute('''
                UPDATE users 
                SET email = %s, first_name = %s, last_name = %s, location = %s 
                WHERE user_id = %s''', 
                (email, first_name, last_name, location, session['user_id']))
            db.get_db().commit()
            flash('Profile updated successfully!', 'success')

    with db.get_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
        user = cursor.fetchone()
    
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    """Logout endpoint.

    Methods:
    - get: Logs the current user out (if they were logged in to begin with),
        and redirects them to the login page.
    """
    # Note that nothing actually happens on the server when a user logs out: we
    # just remove the cookie from their web browser. They could technically log
    # back in by manually restoring the cookie we've just deleted. In a high-
    # security web app, you may need additional protections against this (e.g.
    # keeping a record of active sessions on the server side).
    session.clear()
    
    return redirect(url_for('login'))