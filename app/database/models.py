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

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base


class AdminToken(Base):
    """
    This class represents the AdminToken table in the database.
    It stores the access token, refresh token, and other related information for the admin user.
    """
    __tablename__ = 'admin_tokens'
    id = Column(Integer, primary_key=True, index=True)  # Primary key - index
    access_token = Column(String, nullable=False)   # Webex access token for the admin user
    expires_in = Column(Integer)    # Expiry time for the access token
    refresh_token = Column(String)      # Webex refresh token for the admin user
    refresh_token_expires_in = Column(Integer)  # Expiry time for the refresh token
    token_type = Column(String)    # Type of token
    scope = Column(String)   # Scope of the token
    expires_at = Column(Float)  # Expiry time for the access token
    session_token = Column(String, nullable=False)    # Web session token for the admin user


class UserList(Base):
    """
    This class represents the UserList table in the database.
    It stores the user_id and session_token for each user.
    """
    __tablename__ = 'user_list'
    user_id = Column(String, primary_key=True, index=True)  # Primary key - Webex User ID
    session_token = Column(String, nullable=False)  # Web session token for the user


class AllowList(Base):
    """
    This class represents the AllowList table in the database.
    It stores the user_id and a boolean indicating if the user is allowed to make calls.
    It also has a relationship with the TimeLocation table.
    """
    __tablename__ = 'allow_list'
    user_id = Column(String, primary_key=True, index=True)  # Primary key - Webex User ID
    allow_caller = Column(Boolean, default=False)   # Boolean indicating if the user is allowed to make calls
    time_locations = relationship("TimeLocation", back_populates="allow_list")  # Relationship to TimeLocation


class TimeLocation(Base):
    """
    This class represents the TimeLocation table in the database.
    It stores the user_id, session_token, time, latitude, longitude, and last_update for each user.
    It also has a relationship with the AllowList table.
    """
    __tablename__ = 'time_locations'
    id = Column(Integer, primary_key=True, index=True)  # Primary key - index
    user_id = Column(String, ForeignKey('allow_list.user_id'), nullable=False)  # Foreign key to UserList - Webex User ID
    session_token = Column(String, nullable=False)  # Web session token for the user
    time = Column(String, nullable=False)   # Time of the location update
    latitude = Column(Float, nullable=False)    # Latitude of the location
    longitude = Column(Float, nullable=False)   # Longitude of the location
    last_update = Column(Float, nullable=False)     # Last update time
    allow_list = relationship("AllowList", back_populates="time_locations")  # Relationship to AllowList
