from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from loginapp import app, db, flask_bcrypt
import os
from werkzeug.utils import secure_filename

# Create a blueprint for profile-related routes
profile_bp = Blueprint('profile', __name__)

# Configure upload folder for profile images
UPLOAD_FOLDER = 'loginapp/static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/profile')
def view_profile():
    """View the current user's profile."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Get the user's profile from the database
    with db.get_cursor() as cursor:
        cursor.execute('''
            SELECT user_id, username, email, first_name, last_name, location, profile_image, role, status
            FROM users
            WHERE user_id = %s
        ''', (session['id'],))
        user = cursor.fetchone()
    
    return render_template('profile/view.html', user=user)

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Edit the current user's profile."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Get the user's current profile
    with db.get_cursor() as cursor:
        cursor.execute('''
            SELECT user_id, username, email, first_name, last_name, location, profile_image
            FROM users
            WHERE user_id = %s
        ''', (session['id'],))
        user = cursor.fetchone()
    
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        location = request.form.get('location', '').strip()
        
        # Validate form data
        errors = {}
        if not email:
            errors['email'] = 'Email is required'
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors['email'] = 'Please enter a valid email address'
        
        if not first_name:
            errors['first_name'] = 'First name is required'
        elif len(first_name) > 50:
            errors['first_name'] = 'First name must be 50 characters or less'
        
        if not last_name:
            errors['last_name'] = 'Last name is required'
        elif len(last_name) > 50:
            errors['last_name'] = 'Last name must be 50 characters or less'
        
        if not location:
            errors['location'] = 'Location is required'
        elif len(location) > 50:
            errors['location'] = 'Location must be 50 characters or less'
        
        # Handle profile image upload
        profile_image = user['profile_image']  # Default to current image
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{session['id']}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                profile_image = f"uploads/profiles/{filename}"
        
        if errors:
            return render_template('profile/edit.html', user=user, errors=errors)
        
        # Update the user's profile in the database
        with db.get_cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET email = %s, first_name = %s, last_name = %s, location = %s, profile_image = %s
                WHERE user_id = %s
            ''', (email, first_name, last_name, location, profile_image, session['id']))
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile.view_profile'))
    
    return render_template('profile/edit.html', user=user)

@profile_bp.route('/profile/change-password', methods=['GET', 'POST'])
def change_password():
    """Change the current user's password."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate form data
        errors = {}
        
        # Get the user's current password hash
        with db.get_cursor() as cursor:
            cursor.execute('SELECT password_hash FROM users WHERE user_id = %s', (session['id'],))
            result = cursor.fetchone()
            current_hash = result['password_hash']
        
        # Verify current password
        if not flask_bcrypt.check_password_hash(current_hash, current_password):
            errors['current_password'] = 'Current password is incorrect'
        
        # Validate new password
        if len(new_password) < 8:
            errors['new_password'] = 'New password must be at least 8 characters long'
        
        # Confirm passwords match
        if new_password != confirm_password:
            errors['confirm_password'] = 'Passwords do not match'
        
        if errors:
            return render_template('profile/change_password.html', errors=errors)
        
        # Update the password
        password_hash = flask_bcrypt.generate_password_hash(new_password)
        with db.get_cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET password_hash = %s
                WHERE user_id = %s
            ''', (password_hash, session['id']))
        
        flash('Password changed successfully', 'success')
        return redirect(url_for('profile.view_profile'))
    
    return render_template('profile/change_password.html')

# Register the blueprint with the app
app.register_blueprint(profile_bp) 