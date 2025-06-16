from api import create_app
# import time # No longer needed here for sync
from api.jira_issue.service import start_background_sync, stop_background_sync # Modified import
import atexit # To stop the thread gracefully on exit

if __name__ == '__main__':
   
    # Create and run the application
    app = create_app()

    # Start the background sync scheduler
    start_background_sync()

    # Register a function to stop the sync thread when the application exits
    atexit.register(stop_background_sync)

    # The app.run() call is blocking, so scheduler must be started before it.
    app.run(threaded=True,host='0.0.0.0', port=8080)