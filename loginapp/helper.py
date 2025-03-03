from loginapp import app
from loginapp import db
from flask import redirect, render_template, session, url_for

@app.route('/helper/home')
def helper_home():
    """Helper Homepage endpoint.

    Methods:
    - get: Renders the homepage for the current helper, or an "Access
         Denied" 403: Forbidden page if the current user has a different role.

    If the user is not logged in, requests will redirect to the login page.
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif session['role'] != 'helper':
        return render_template('access_denied.html'), 403

    with db.get_cursor() as cursor:
        # Get current user data
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['user_id'],))
        user = cursor.fetchone()

        # Get issue statistics
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM issues
            GROUP BY status
        ''')
        stats = {
            'new': 0,
            'open': 0,
            'stalled': 0,
            'resolved': 0
        }
        for row in cursor.fetchall():
            stats[row['status']] = row['count']

    return render_template('helper_home.html', user=user, stats=stats) 