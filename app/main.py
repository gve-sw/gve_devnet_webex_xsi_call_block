"""
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Mark Orszycki <morszyck@cisco.com>"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

from fastapi import FastAPI
import uvicorn
from routes import webex_router
from config.config import c
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from logger.logrr import lm
from starlette.middleware.sessions import SessionMiddleware
from databases import Database
from sqlalchemy import create_engine
from app.database.models import Base
from call_monitor import start_call_monitoring


def create_app() -> FastAPI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allows use of localhost for testing Oauth flow
    fastapi_app = FastAPI(title=c.APP_NAME, version=c.APP_VERSION)  # Create the FastAPI app

    # Add CORS middleware
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development, use ["*"]. For production, specify your frontend's domain
        allow_credentials=True,  # Allows cookies
        allow_methods=["*"],  # Specifies the methods (GET, POST, etc.) allowed
        allow_headers=["*"],  # Allows all headers
    )

    database = Database(c.SQLALCHEMY_DATABASE_URL)  # Create the database object
    engine = create_engine(c.SQLALCHEMY_DATABASE_URL)  # Create the database engine

    @fastapi_app.on_event("startup")
    async def on_startup():
        lm.print_start_panel(app_name=c.APP_NAME)  # Print the start info message to console
        lm.print_admin_start_panel(public_url=c.PUBLIC_URL)  # Print the start info message to console
        # lm.print_config_table(config_instance=c)  # Print the config table to console
        await database.connect()  # Connect to the database
        Base.metadata.create_all(bind=engine)  # Create tables in the database

        # Uncomment the following lines to start call monitoring upon app startup if admin token in DB is present & valid
        # try:
        #     await start_call_monitoring()
        # except Exception as e:
        #     lm.error(f"Error starting call monitoring: {e}")
        fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")  # Serve static files

    @fastapi_app.on_event("shutdown")
    async def on_shutdown():
        lm.print_exit_panel()  # Print the exit info message to console
        await database.disconnect()  # Disconnect from the database

    fastapi_app.include_router(webex_router)  # Include the router
    fastapi_app.add_middleware(SessionMiddleware, secret_key=c.APP_SECRET_KEY)  # Add session middleware
    return fastapi_app


app = create_app()  # Create the FastAPI app

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="critical", reload=True)
