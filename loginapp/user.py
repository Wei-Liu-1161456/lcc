from loginapp import app
from loginapp import db
from flask import redirect, render_template, request, session, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
import MySQLdb.cursors
import re
import os
from werkzeug.utils import secure_filename

# Create an instance of the Bcrypt class, which we'll be using to hash user
# passwords during login and registration.
flask_bcrypt = Bcrypt(app)

# Default role for new users
DEFAULT_USER_ROLE = 'visitor'

# Password validation pattern
# At least 8 characters, must include uppercase, lowercase, and numbers
PASSWORD_PATTERN = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

# Add these constants at the top of the file
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join('loginapp', 'static', 'uploads', 'profiles')
DEFAULT_AVATAR = '300.jpeg'

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()

        if user and flask_bcrypt.check_password_hash(user['password_hash'], password):
            if user['status'] != 'active':
                flash('Your account is inactive. Please contact an administrator for assistance.', 'danger')
                return render_template('login.html', username=username, error=True)
                
            session['loggedin'] = True
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['first_name'] = user['first_name']
            session['profile_image'] = user['profile_image']
            
            return redirect(user_home_url())
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html', username=username, error=True)

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

                # Store registration data in session for auto-fill login
                session['registration_data'] = {
                    'username': form_data['username'],
                    'password': form_data['password'],
                    'show_welcome': True
                }

                # Use success category for success messages
                flash('Account created successfully! Please log in with your credentials.', 'success')
                return redirect(url_for('login'))

    # GET request or form validation failed - show form
    return render_template('signup.html', errors=errors, **form_data)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """User Profile page endpoint."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    errors = {}

    if request.method == 'POST':
        form_data = {
            'email': request.form['email'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'location': request.form['location']
        }

        # Validate form data...
        if not errors:
            # Handle profile image upload if provided
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and file.filename != '':
                    filename = f"{session['username']}_image{os.path.splitext(file.filename)[1]}"
                    filename = secure_filename(filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    form_data['profile_image'] = filename

            # Update user profile
            with db.get_cursor() as cursor:
                update_fields = ['email', 'first_name', 'last_name', 'location']
                query_parts = [f"{field} = %s" for field in update_fields]
                values = [form_data[field] for field in update_fields]
                
                if 'profile_image' in form_data:
                    query_parts.append("profile_image = %s")
                    values.append(form_data['profile_image'])
                
                values.append(session['user_id'])
                
                cursor.execute(
                    f'UPDATE users SET {", ".join(query_parts)} WHERE user_id = %s',
                    values
                )
                db.get_db().commit()
                flash('Profile updated successfully!', 'success')
                # Redirect to user's home page instead of profile
                return redirect(user_home_url())

    # Get current user data
    with db.get_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
        user = cursor.fetchone()
    
    # Clear any existing flash messages when just viewing the profile
    session.pop('_flashes', None)
    return render_template('profile.html', user=user, errors=errors)

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

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'loggedin' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    with db.get_cursor() as cursor:
        cursor.execute('SELECT password_hash FROM users WHERE user_id = %s', 
                      (session['user_id'],))
        user = cursor.fetchone()

    if not flask_bcrypt.check_password_hash(user['password_hash'], current_password):
        return jsonify({
            'success': False,
            'error': 'Current password is incorrect'
        })

    if not re.match(PASSWORD_PATTERN, new_password):
        return jsonify({
            'success': False,
            'error': 'Password must be at least 8 characters and include uppercase, lowercase, and numbers'
        })

    # Update password
    hashed_password = flask_bcrypt.generate_password_hash(new_password)
    with db.get_cursor() as cursor:
        cursor.execute('UPDATE users SET password_hash = %s WHERE user_id = %s',
                      (hashed_password, session['user_id']))
        db.get_db().commit()

    return jsonify({
        'success': True,
        'message': 'Password updated successfully!'
    })

@app.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    """Handle profile image upload."""
    if 'loggedin' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    if 'profile_image' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['profile_image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})

    if file:
        # Create filename using username
        filename = f"{session['username']}_image{os.path.splitext(file.filename)[1]}"
        filename = secure_filename(filename)
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Update database
        with db.get_cursor() as cursor:
            cursor.execute('UPDATE users SET profile_image = %s WHERE user_id = %s',
                         (filename, session['user_id']))
            db.get_db().commit()
        
        return jsonify({'success': True, 'filename': filename})

    return jsonify({'success': False, 'error': 'File upload failed'})

@app.route('/delete_profile_image', methods=['POST'])
def delete_profile_image():
    """Delete user's profile image."""
    if 'loggedin' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    with db.get_cursor() as cursor:
        # Get current profile image
        cursor.execute('SELECT profile_image FROM users WHERE user_id = %s',
                      (session['user_id'],))
        result = cursor.fetchone()
        
        if result and result['profile_image']:
            # Delete file if it exists
            file_path = os.path.join(UPLOAD_FOLDER, result['profile_image'])
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Update database
            cursor.execute('UPDATE users SET profile_image = NULL WHERE user_id = %s',
                         (session['user_id'],))
            db.get_db().commit()

    return jsonify({'success': True})

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile endpoint."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    errors = {}
    form_data = {
        'email': request.form['email'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'location': request.form['location']
    }

    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', form_data['email']):
        errors['email'] = 'Please enter a valid email address'

    # Validate required fields
    if not form_data['first_name'].strip():
        errors['first_name'] = 'First name is required'
    if not form_data['last_name'].strip():
        errors['last_name'] = 'Last name is required'
    if not form_data['location'].strip():
        errors['location'] = 'Location is required'

    # Check if email is already taken by another user
    with db.get_cursor() as cursor:
        cursor.execute('SELECT user_id FROM users WHERE email = %s AND user_id != %s',
                      (form_data['email'], session['user_id']))
        if cursor.fetchone():
            errors['email'] = 'This email is already registered'

    if errors:
        with db.get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
            user = cursor.fetchone()
        return render_template('profile.html', user=user, errors=errors)

    # Update user profile
    with db.get_cursor() as cursor:
        cursor.execute('''
            UPDATE users 
            SET email = %s, first_name = %s, last_name = %s, location = %s 
            WHERE user_id = %s
        ''', (form_data['email'], form_data['first_name'], 
              form_data['last_name'], form_data['location'], 
              session['user_id']))
        db.get_db().commit()

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('profile'))