from loginapp import app
from loginapp import db
from flask import redirect, render_template, session, url_for

@app.route('/visitor/home')
def visitor_home():
    """Visitor Homepage endpoint.

    Methods:
    - get: Renders the homepage for the current visitor, or an "Access
         Denied" 403: Forbidden page if the current user has a different role.

    If the user is not logged in, requests will redirect to the login page.
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif session['role'] != 'visitor':
        return render_template('access_denied.html'), 403

    # Get current user data
    with db.get_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
        user = cursor.fetchone()

    return render_template('visitor_home.html', user=user) 