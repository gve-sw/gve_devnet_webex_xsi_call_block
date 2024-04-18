# gve_devnet_webex_xsi_call_block
This program utilizes Webex's External Service Interface (XSI) events and real-time geolocation tracking to dynamically manage call permissions within an organization, allowing or blocking calls based on users' compliance with predefined geographical boundaries. Leveraging OAuth for secure authentication and JavaScript for continuous geolocation updates, it ensures that only authorized users within specific locations can initiate or receive calls, enhancing the organization's security and compliance posture.

## Contacts
* Mark Orszycki
* Gerardo Chaves

## Features
- Monitoring and managing call events in real-time using Webex XSI events
- OAuth for secure authentication and user identification
- Continuous geolocation updates / tracking using JavaScript - sends geolocation updates to the server every 30 seconds
- Dynamic call permission management based on geolocation data
- Blocking calls for users outside predefined geographical boundaries
- Secure session management and token refresh for continuous application use
- Database operations using SQLAlchemy for data storage and retrieval
- PostgreSQL database for storing user data, session tokens, and geolocation information

## Solution Overview
### Admin Starting Point: Environment Setup
* Administrators start the setup process for the application, which includes creating and loading environment variables.
* The setup process is initiated by first navigating to /setup with `cd setup` & running the run command `python setup.py run`. This command manages environment variable configuration & project setup using the EM Class. This class provides methods to create and load the .env file, prompt for env variables if missing, reload the environment, validate environment variables, and set environment variables.
* This includes setting up the Webex Integration Client ID and Client Secret, the required scope of access, the public URL of the application, and the geolocation boundaries for call permissions. (refer to setup gif below)
* Once the environment variables are set, the application is ready to run with the necessary configurations.
* To run the application, return to root directory with `cd ..`, navigate to the app directory with `cd app`, & run the FastAPI application with `uvicorn main:app`.
* Login to admin/login route with your Webex credentials to access the admin dashboard & initiate call monitoring.
* If the server restarts, the application will automatically reload the environment variables from the .env file and call monitoring will resume.
* If the server is stopped, call monitoring will resume on restart as long as the admin token is still valid.

### User Starting Point: The Webex Shortcut
* Users access the application through a Webex shortcut that directs them to the application's /user/login. This serves as the entry point to the system, differentiating between user and admin functionalities.

### User Authentication and Geolocation Tracking
* Upon clicking the shortcut, users are prompted to log in through a Webex OAuth flow, ensuring secure access based on their role.
* After successful authentication, users land on a page where they're asked to share their geolocation. This crucial step enables the application to track the user's location in real-time.
* The application continues to send geolocation updates to the server every 30 seconds. This persistent tracking is key to the dynamic management of call permissions.

### Dynamic Call Permissions Based on Geolocation
* The system uses the continuously updated geolocation data to make real-time decisions about call permissions. If a user's location is detected outside predefined country bounds, any outgoing or incoming calls are automatically blocked.
* This geolocation-based call blocking mechanism ensures that only users within specific geographical boundaries can make or receive calls, adhering to regulatory compliance and enhancing security.

### Backend Processing and Secure Session Management
* The application's backend is responsible for handling OAuth callbacks, managing session tokens securely, processing geolocation updates, and monitoring call events.
* It captures and processes call events, applying logic based on user permissions and geolocation to allow, reject, or terminate calls accordingly.

### Database Operations & Models
* The application uses SQLAlchemy to interact with the database. It provides CRUD operations for different tables such as AdminToken, UserList, AllowList, and TimeLocation.
* The application uses SQLAlchemy ORM to define models for the AdminToken, UserList, AllowList, and TimeLocation tables.
* The AdminToken model stores the admin token, which is used to authenticate the admin user and initiate call monitoring.
* The UserList model stores the user's Webex ID, email, and geolocation data.
* The AllowList model stores the user's Webex ID, and if they are allowed to make calls.
* The TimeLocation model stores the user's Webex ID, if they are allowed to make calls, and their geolocation data.
* These models are used to store and retrieve data from the database, enabling dynamic call permission management based on user roles and geolocation.
* SQLAlchemy engine and session configurations used to interact with the database, ensuring data integrity and consistency.
* Pydantic models used for data validation and serialization, ensuring that the data passed between the frontend and backend is accurate and secure.

### Logging and Console Output
* The application uses the LoggerManager class to manage logging and console output. This class provides methods for setting up the logger, thread-safe printing, logging and printing messages, and displaying data in a rich table format.
* Once 'call monitoring' has been initiated, a queue of Webex Calling Events will be logged to /app/logger/logs/app.log & displayed to the console, showing the call events that have been processed by the application.
* The LoggerManager class ensures that the application's logging and console output are well-organized, making it easier to track and debug call events and geolocation updates.
* The LoggerManager class also provides a rich table format for displaying data, making it easier to read and understand the application's output.

## Key Components
- **Cisco Webex**: A cloud-based collaboration platform that provides video conferencing, team messaging, and file sharing, used here to authenticate users and manage call events.
- **Cisco Webex XSI**: A RESTful API that provides access to call control and call event data, used here to monitor and manage call events in real-time.
- **Cisco Webex OAuth**: An authentication mechanism that allows users to log in to the application securely using their Webex credentials.
- **Cisco Webex Integration**: A mechanism that allows the application to access the Webex REST API on behalf of another Webex Teams user, used here to request permission to invoke the Webex REST API.
- **Python**: The primary programming language for the application.
- **FastAPI**: A modern, high-performance web framework for building APIs with Python, used here for creating the web interface and managing API requests and responses.
- **Uvicorn**: An efficient ASGI server implementation for Python, responsible for running the FastAPI application with excellent performance and concurrency handling.
- **Jinja2**: A powerful template engine for Python, employed to render dynamic HTML templates, for consistent application user interface.
- **HTML & CSS**: HTML provides the structure for web pages, while CSS is used for layout and design.
- **JavaScript**: Used to track geolocation updates and send them to the server in real-time.
- **PostgreSQL Database**: A powerful, open-source relational database system, used here to store user data, session tokens, and geolocation information.
- **SQLAlchemy**: A powerful SQL toolkit and Object-Relational Mapping (ORM) library for Python, used to interact with the SQLite database.
- **Docker**: A platform for developing, shipping, and running applications in containers, used to package the application and its dependencies into a standardized unit for software development.

## Prerequisites
### Webex Prerequisites 
**Webex API Access Token**:
1. To use the Webex REST API, you need a Webex account backed by Cisco Webex Common Identity (CI). If you already have a Webex account, you're all set. Otherwise, go ahead and [sign up for a Webex account](https://cart.webex.com/sign-up).
2. When making request to the Webex REST API, the request must contain a header that includes the access token. A personal access token can be obtained [here](https://developer.webex.com/docs/getting-started).
3. Retrieve your PAT. This will be used during the setup process to fetch the admin Webex user ID; user ID is used to verify admin when attempting to initiate call monitoring.

**OAuth Integrations**: 
1. Integrations are how you request permission to invoke the Webex REST API on behalf of another Webex Teams user. To do this in a secure way, the API supports the OAuth2 standard which allows third-party integrations to get a temporary access token for authenticating API calls instead of asking users for their password. To register an integration with Webex Teams:
2. Log in to `developer.webex.com`
3. Click on your avatar at the top of the page and then select `My Webex Apps`
4. Click `Create a New App`
5. Click `Create an Integration` to start the wizard
6. Follow the instructions of the wizard and provide your integration's name, description, and logo
7. After successful registration, you'll be taken to a different screen containing your integration's newly created Client ID and Client Secret
8. Copy the secret and store it safely. Please note that the Client Secret will only be shown once for security purposes
9. Note that access token may not include all the scopes necessary for this prototype by default. To include the necessary scopes, select `My Webex Apps` under your avatar once again. Then click on the name of the integration you just created. Scroll down to the `Scopes` section. From there, select all the scopes needed for this integration.
10. To read more about Webex Integrations & Authorization and to find information about the different scopes, you can find information [here](https://developer.webex.com/docs/integrations)
11. Configure the following scopes for the Webex Integration: `spark:all,spark-admin:xsi,spark:xsi,spark-admin:locations_read,spark-admin:people_read,spark-admin:licenses_read`

### PostgreSQL Database Installation
1. PostgreSQL is used as the database for this application. You can download PostgreSQL [here](https://www.postgresql.org/download/). (If you fancy a Homebrew, see the instructions below.)
2. Create a database in PostgreSQL and update the database URL in the .env file: `SQLALCHEMY_DATABASE_URL="postgresql://YOUR_USN:YOUR_PASSWORD@localhost/YOUR_DB_NAME"`

#### Optional: PostgreSQL Installation with Homebrew
*PostgreSQL install with Homebrew:*
1.  PostgreSQL Install & Setup with Homebrew
```script
brew install postgresql    // Install PostgreSQL with Homebrew
brew services start postgresql   // Start the PostgreSQL service
postgres -V
psql -d postgres  
CREATE ROLE some_test_user WITH LOGIN SUPERUSER; 
ALTER ROLE some_test_user WITH PASSWORD 'YOUR_NEW_PASSWORD'; 
\q
psql -U some_test_user postgres
CREATE DATABASE webex_call_blocking;
```

2. PostgreSQL Commands
```script
psql -U postgres  // Connect to the default database with the new role
\l // List all databases
\c YOUR_DB_NAME // Connect to a specific database
\dt // List all tables in the current database
SELECT * FROM YOUR_TABLE_NAME; // Query a table
DELETE FROM YOUR_TABLE_NAME; // Delete all rows from a table

```
*Note: SQLAlchemy Database URL: `SQLALCHEMY_DATABASE_URL="postgresql://postgres:YOUR_PASSWORDWlocalhost/YOUR_DB_NAME"`*

## Installation/Configuration
1. Clone this repository with `git clone https://github.com/gve-sw/gve_devnet_webex_call_block.git`
2. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
3. Install the requirements into virtual environment with 'pip3 install -r requirements.txt'
4. Run the setup script to configure the environment variables and project setup:
   ```script
   cd app/config
   python setup.py run
   ```
5. Once setting all .env variables and settings.py, start the FastAPI application with the following command:
   ```script
    uvicorn main:app
    ```

### Option: Manually Create and Update the `.env` & update settings.py file:
If you prefer to manually create and update the `.env` file instead of using the setup script, follow these steps:
To configure the application, you need to update the `.env` file with the appropriate values. 
This file contains key settings that the application uses to interact with the Webex APIs and to set up its environment.
#### Manually Setting Up the `.env` File:
1. **Create & update .env in app/config/**:
   ```script
   cd app/config
   touch .env
   open .env
   ```
2. **Client ID and Secret**:
   - `CLIENT_ID`: Your Webex Integration Client ID.
   - `CLIENT_SECRET`: Your Webex Integration Client Secret.
3. **Webex Admin User ID**:
   - `WEBEX_ADMIN_UID`: The Webex admin user ID. This is used to fetch the Webex organization's details and used to verify the user's role in the organization after authentication.
4. **Database Configuration**:
   - `SQLALCHEMY_DATABASE_URL`: The database URL for the application. The default is a PostgreSQL database, but you can replace it with a different database URL if needed.

#### Manually Setting Up the `settings.py` File:
1. **Configure Geolocation Boundaries**: 
   - `LAT_MAX`: `LAT_MIN`, `LAT_MAX`, `LON_MIN`, `LON_MAX` are the latitude and longitude boundaries for the geofencing feature. Update these in settings.py as well.
2. **Geolocation Timeout**:
    - `GEOLOCATION_TIMEOUT`: The time interval (in seconds) for sending geolocation updates to the server. The default is 300 seconds.

Once you have updated and saved the `.env` file with the correct values, the application will be configured to run with these settings.
Example `.env`:
   ```script
   WEBEX_ADMIN_UID=YOUR_WEBEX_ADMIN_UID
   CLIENT_ID=YOUR_WEBEX_INTEGRATION_CLIENT_ID
   CLIENT_SECRET=YOUR_WEBEX_INTEGRATION_CLIENT_SECRET
   SQLALCHEMY_DATABASE_URL="postgresql://YOUR_USN:YOUR_PASSWORD@localhost/YOUR_DB_NAME"
   ```

Example settings.py:
```script
# Required Environment Variables (app/config/.env file)
REQUIRED_ENV_VARS: List[str] = ['WEBEX_ADMIN_UID', 'CLIENT_ID', 'CLIENT_SECRET', 'SQLALCHEMY_DATABASE_URL']

# Required Settings
REQUIRED_SETTINGS: List[str] = ['LAT_MIN', 'LAT_MAX', 'LON_MIN', 'LON_MAX', 'GEOLOCATION_TIMEOUT']

# FastAPI Settings
APP_NAME: str = 'Webex Call Blocking by Geolocation'
APP_VERSION: str = 'POC v1.0'
UVICORN_LOG_LEVEL: str = 'WARNING'

# Webex Integration URLs
AUTHORIZATION_BASE_URL = 'https://api.ciscospark.com/v1/authorize'
TOKEN_URL = 'https://api.ciscospark.com/v1/access_token'
WEBEX_BASE_URL = 'https://webexapis.com/v1/'
SCOPE: List[str] = ['spark:all,spark-admin:xsi,spark:xsi,spark-admin:locations_read,spark-admin:people_read,spark-admin:licenses_read']
PUBLIC_URL: str = 'http://127.0.0.1:8000'

# Geolocation bounding boxes &
LAT_MIN: float = 10.0
LAT_MAX: float = 20.0
LON_MIN: float = 100.0
LON_MAX: float = 30.1
GEOLOCATION_TIMEOUT: int = 20
```

## Usage
### Start the Application
To initiate the prototype, start the FastAPI application:
```
$ cd app
$ uvicorn main:app
$ uvicorn main:app --log-level warning
```

## Application Structure
The application is structured into several Python files and HTML templates:
- `app/`: Contains the main application code, including the FastAPI application and the Webex event handling logic.
- `main.py`: The main entry point of the application. It handles the routing and main logic of the application.
- `routes.py`: Contains the FastAPI routes for the application's API.
- `schemas.py`: Contains Pydantic models for data validation and serialization.
- `call_monitor.py`: Contains the logic for monitoring and processing call events using the Webex XSI events.
- `funcs.py`: Contains helper functions used throughout the application.
- `db.py`: Contains the SQLAlchemy engine and session configurations.
- `models.py`: Contains the SQLAlchemy ORM models for the application's database.
- `crud.py`: Contains the CRUD operations for the application's database.
- `logger/`: Contains the LoggerManager class for managing logging and console output.
- `templates/`: Contains the HTML templates for the application's frontend.
- `static/`: Contains the static files (e.g., CSS, JavaScript) for the application's frontend.
- `Dockerfile`: Contains the Docker configuration for building the application image.
- `docker-compose.yml`: Contains the Docker Compose configuration for running the application.
- `setup/`: Contains the setup script for configuring the environment variables.
- `config/`: Contains the configuration files for the application.
- `.env/`: Will need to be created in the config folder to store environment variables.

## Screenshots/GIFs
### Environment Variables & Settings Setup: <br>
![/IMAGES/setup.gif](/IMAGES/setup.gif)<br>

### PostgreSQL Setup:
![/IMAGES/psql_setup.gif](/IMAGES/psql_setup.gif)<br>

### Webex Calling Event Monitoring Setup:
![/IMAGES/call_monitor.gif](/IMAGES/call_monitor.gif)<br>


## Additional Information
### Token Management
*Webex Token Management:*
> Access Token (14 days): Used for authenticating API requests. Checked for validity and refreshed as needed.
> Refresh Token (90 days): Used to obtain a new access token when the current one expires. Checked for its expiry and triggers re-authentication if expired.
> Admin token PostgreSQL database, allowing call monitoring initiation upon server restart with re-authentication.

### Troubleshooting
* If you encounter any issues with the application, please refer to the logs in the `app/logger/logs` directory for more information.

### LICENSE
Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT
Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING
See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use 
"AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance.
Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough 
testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.




