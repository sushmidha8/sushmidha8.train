from app import create_app
from app.models import db, User, Train, Schedule, Booking
import os
from gevent import monkey
from werkzeug.middleware.proxy_fix import ProxyFix

# Apply gevent monkey patches
monkey.patch_all()

# Create application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'config.DevelopmentConfig')

# Configure proxy headers
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)

# Shell context for Flask CLI
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Train': Train,
        'Schedule': Schedule,
        'Booking': Booking
    }

# Application entry point
if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # Production logging configuration
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Ensure logs directory exists
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Configure file logging
    file_handler = RotatingFileHandler(
        'logs/railway.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Add handlers
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Train Booking System startup')