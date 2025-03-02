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
    """Sign up endpoint.

    Methods:
    - get: Shows the sign up form.
    - post: Processes the sign up form submission.
    """
    # Initialize empty errors dict
    errors = {}
    # Initialize form data variables
    form_data = {
        'username': '',
        'email': '',
        'first_name': '',
        'last_name': '',
        'location': ''
    }

    if request.method == 'POST':
        # Get form data
        form_data = {
            'username': request.form['username'],
            'email': request.form['email'],
            'password': request.form['password'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'location': request.form['location']
        }

        # Validate username
        if not re.match(r'^[A-Za-z0-9_-]{3,20}$', form_data['username']):
            errors['username'] = 'Username must be 3-20 characters and contain only letters, numbers, underscores, and hyphens'

        # Validate email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', form_data['email']):
            errors['email'] = 'Please enter a valid email address'

        # Validate password
        if not re.match(PASSWORD_PATTERN, form_data['password']):
            errors['password'] = 'Password must be at least 8 characters and include uppercase, lowercase, and numbers'

        # Validate first_name and last_name
        if not form_data['first_name'].strip():
            errors['first_name'] = 'First name is required'
        if not form_data['last_name'].strip():
            errors['last_name'] = 'Last name is required'

        # Validate location
        if not form_data['location'].strip():
            errors['location'] = 'Location is required'

        # Check if username already exists
        with db.get_cursor() as cursor:
            # Check username
            cursor.execute('SELECT * FROM users WHERE username = %s', (form_data['username'],))
            if cursor.fetchone():
                errors['username'] = 'Username already exists'

            # Check email
            cursor.execute('SELECT * FROM users WHERE email = %s', (form_data['email'],))
            if cursor.fetchone():
                errors['email'] = 'Email already registered'

            # If no errors, create the account
            if not errors:
                # Hash the password
                hashed_password = flask_bcrypt.generate_password_hash(form_data['password'])
                
                # Store new user in database
                cursor.execute(
                    'INSERT INTO users (username, password_hash, email, role, first_name, last_name, location, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (form_data['username'], hashed_password, form_data['email'], DEFAULT_USER_ROLE,
                     form_data['first_name'], form_data['last_name'], form_data['location'], 'active')
                )
                db.get_db().commit()

                # Redirect to login page with success message
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))

    # GET request or form validation failed - show form
    return render_template('signup.html', errors=errors, **form_data)

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