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

from datetime import datetime, timezone, timedelta
from threading import local

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.logger.logrr import lm
from app.database.models import AdminToken, UserList, AllowList, TimeLocation


def extract_access_token(token_object):
    """ Extract Webex access token from token object """
    if token_object and "access_token" in token_object:
        return token_object["access_token"]
    else:
        raise ValueError("Access token not found in the provided token object.")


class CRUDOperations:
    """
    Class for performing CRUD operations on the database.

    Attributes:
        _instance (CRUDOperations): The instance of the CRUDOperations class.
        _local (local): The threading.local object.
    """
    _instance = None
    _local = local()

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(CRUDOperations, cls).__new__(cls)
        return cls._instance

    def __init__(self, db: Session):
        self._local.db = db

    @property
    def db(self):
        return self._local.db

    def commit_db(self, db_item, operation_name):
        """
        Common command call. Commits the db_item to the database and handles any SQLAlchemyError.

        Args:
            db_item: The database item to commit.
            operation_name (str): The name of the operation being performed.
        """
        self.db.add(db_item)
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            lm.lnp(f"Error occurred while committing {operation_name} to the database: {e}")
        return db_item

    def create_admin_token(self, access_token: str, expires_in: int, refresh_token: str, refresh_token_expires_in: int, token_type: str,
                           scope: list, expires_at: float, session_token: str):
        """
        Creates a new AdminToken entry in the database.

        Args:
            access_token (str): The access token.
            expires_in (int): The duration in seconds that the access token is valid.
            refresh_token (str): The refresh token.
            refresh_token_expires_in (int): The duration in seconds that the refresh token is valid.
            token_type (str): The type of the token.
            scope (str): The scope of the token.
            expires_at (float): The timestamp when the token expires.
        """
        # Convert the scope list to a string
        scope_str = ' '.join(scope)

        db_item = AdminToken(
            access_token=access_token,
            expires_in=expires_in,
            refresh_token=refresh_token,
            refresh_token_expires_in=refresh_token_expires_in,
            token_type=token_type,
            scope=scope_str,
            expires_at=expires_at,
            session_token=session_token,
        )
        return self.commit_db(db_item=db_item, operation_name='create_admin_token')

    def read_admin_token(self):
        """
        Retrieves the AdminToken entry from the database.
        """
        admin_token_entry = self.db.query(AdminToken).first()
        if admin_token_entry is not None:
            admin_token_data = {
                "access_token": admin_token_entry.access_token,
                "expires_in": admin_token_entry.expires_in,
                "refresh_token": admin_token_entry.refresh_token,
                "refresh_token_expires_in": admin_token_entry.refresh_token_expires_in,
                "token_type": admin_token_entry.token_type,
                "scope": admin_token_entry.scope,
                "expires_at": admin_token_entry.expires_at,
                "session_token": admin_token_entry.session_token
            }
            # lm.lnp(f"Retrieved admin token from the database: {admin_token_data}")
            return admin_token_data
        else:
            lm.lnp("No admin token entry found.", level="warning", style="warning")
            return None

    def update_admin_token(self, access_token: str, expires_in: int, refresh_token: str, refresh_token_expires_in: int, token_type: str, scope: list, expires_at: float,
                           session_token: str):
        """
        Replaces the admin token in the database. Deletes all existing entries and adds a new one.

        Args:
            access_token (str): The access token.
            expires_in (int): The duration in seconds that the access token is valid.
            refresh_token (str): The refresh token.
            refresh_token_expires_in (int): The duration in seconds that the refresh token is valid.
            token_type (str): The type of the token.
            scope (str): The scope of the token.
            expires_at (float): The timestamp when the token expires.
        """
        self.delete_all_admin_tokens()
        return self.create_admin_token(access_token, expires_in, refresh_token, refresh_token_expires_in, token_type, scope, expires_at, session_token)

    def delete_all_admin_tokens(self):
        """
        Deletes all AdminToken entries from the database.
        """
        self.db.query(AdminToken).delete()
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            lm.lnp(f"Error occurred while deleting all admin tokens from the database: {e}", level="error", style="error")

    def get_admin_access_token(self):
        admin_token_object = self.read_admin_token()
        if not admin_token_object:
            raise ValueError("Admin token object is missing or invalid.")
        return extract_access_token(admin_token_object)

    def create_user_list_entry(self, user_id: str, session_token: str):
        """
        Creates a new UserList entry in the database.

        Args:
            db (Session): The database session.
            user_id (str): The user ID.
            session_token (str): The session token.
        """
        db_item = UserList(
            user_id=user_id,
            session_token=session_token
        )
        return self.commit_db(db_item=db_item, operation_name='create_user_list_entry')

    def read_user_list(self, user_id: str = None, session_token: str = None):
        """
        Retrieves the UserList entry from the database using the user_id or session_token.

        Args:
            user_id (str, optional): The user ID.
            session_token (str, optional): The session token.
        """
        if user_id:
            user_list_entry = self.db.query(UserList).filter(UserList.user_id == user_id).first()
            search_param = user_id
            search_type = 'user ID'
        elif session_token:
            user_list_entry = self.db.query(UserList).filter(UserList.session_token == session_token).first()
            search_param = session_token
            search_type = 'session token'
        else:
            raise ValueError("Either user_id or session_token must be provided.")

        if user_list_entry is not None:
            user_list_data = {
                "user_id": user_list_entry.user_id,
                "session_token": user_list_entry.session_token
            }
            # lm.lnp(f"Retrieved user list from the database: {user_list_data}")
            return user_list_data
        else:
            lm.lnp(f"No user list entry found for the provided {search_type}: {search_param}")
            return None

    def update_user_list_entry(self, user_id: str, session_token: str):
        """
        Updates an existing UserList entry in the database.

        Args:
            db (Session): The database session.
            user_id (str): The user ID.
            session_token (str): The session token.
        """
        db_item = self.db.query(UserList).filter(UserList.user_id == user_id).first()

        if db_item:
            # If a user exists, update the session_token
            db_item.session_token = session_token
            return self.commit_db(db_item=db_item, operation_name='update_user_list_entry')
        else:
            raise ValueError(f"No UserList entry found for user_id: {user_id}")

    def delete_user_list_entry(self, user_id: str):
        """
        Deletes the UserList entry from the database using the user ID.

        Args:
            user_id (str): The user ID.
        """
        # Query for the entry
        db_item = self.db.query(UserList).filter(UserList.user_id == user_id).first()

        # If the entry exists, delete it
        if db_item:
            self.db.delete(db_item)
            return self.commit_db(db_item=db_item, operation_name='delete_user_list_entry')

    def create_allow_list_entry(self, user_id: str, allow_caller: bool):
        """
        Creates a new AllowList entry in the database.

        Args:
            db (Session): The database session.
            user_id (str): The user ID.
            allow_caller (bool): Whether the user is allowed to call.
        """

        db_item = AllowList(
            user_id=user_id, allow_caller=allow_caller
        )
        self.db.add(db_item)
        return self.commit_db(db_item=db_item, operation_name='create_allow_list_entry')

    def update_allow_list_entry(self, user_id: str, allow_caller: bool):
        """
        Updates an existing AllowList entry in the database.

        Args:
            user_id (str): The user ID.
            allow_caller (bool): Whether the user is allowed to call.
        """
        db_item = self.db.query(AllowList).filter(AllowList.user_id == user_id).first()

        if db_item:
            # If a user exists, update the allow_caller
            db_item.allow_caller = allow_caller
            return self.commit_db(db_item=db_item, operation_name='update_allow_list_entry')
        else:
            raise ValueError(f"No AllowList entry found for user_id: {user_id}")

    def read_allow_list(self):
        """
        Retrieves all AllowList entries from the database.
        """
        allow_list_entries = self.db.query(AllowList).all()
        if allow_list_entries:
            allow_list_data = [
                {
                    "user_id": entry.user_id,
                    "allow_caller": entry.allow_caller,
                    "geolocation_data": [
                        {
                            "time": time_location.time,
                            "latitude": time_location.latitude,
                            "longitude": time_location.longitude,
                            "last_update": time_location.last_update
                        }
                        for time_location in entry.time_locations
                    ]
                }
                for entry in allow_list_entries
            ]
            # lm.pp(f"Retrieved allow list from the database: {allow_list_data}")
            return allow_list_data
        else:
            lm.lnp("No allow list entries found.", level="warning", style="warning")
            return None

    def get_allow_list_entry_by_user_id(self, user_id: str):
        """
        Retrieves a specific AllowList entry from the database using the user ID, including the related TimeLocation data.

        Args:
            user_id (str): The user ID for which to retrieve the AllowList entry.

        Returns:
            A dictionary containing the AllowList entry and its related TimeLocation data, or None if not found.
        """
        allow_list_entry = self.db.query(AllowList).filter(AllowList.user_id == user_id).first()  # Query for the entry
        if allow_list_entry:  # If the entry exists
            # Create a dictionary containing the AllowList entry and its related TimeLocation data
            allow_list_data = {
                "user_id": allow_list_entry.user_id,
                "allow_caller": allow_list_entry.allow_caller,
                "geolocation_data": [
                    {
                        "time": time_location.time,
                        "latitude": time_location.latitude,
                        "longitude": time_location.longitude,
                        "last_update": time_location.last_update
                    }
                    for time_location in allow_list_entry.time_locations  # Iterate over the related TimeLocation data
                ]
            }
            # lm.pp(f"Retrieved allow list entry from the database: {allow_list_data}")
            return allow_list_data
        else:
            lm.lnp(f"No allow list entry found for user_id: {user_id}.")
            return None

    def delete_allow_list_entry(self, user_id: str):
        """
        Deletes the AllowList entry from the database using the user ID.

        Args:
            db (Session): The database session.
            user_id (str): The user ID.
        """
        db_item = self.db.query(AllowList).filter(AllowList.user_id == user_id).first()  # Query for the entry

        if db_item:
            self.db.delete(db_item)  # If the entry exists, delete it
            try:
                self.db.commit()  # Commit the deletion
            except Exception as e:
                lm.lnp(f"Error occurred while deleting allow list entry from the database: {e}", level="error", style="error")

    def create_time_location_entry(self, user_id: str, session_token: str, time: str, latitude: float, longitude: float):
        """
        Creates a new TimeLocation entry in the database.

        Args:
            user_id (str): The user ID.
            session_token (str): The session token.
            time (str): The time of the location data.
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.
        """
        db_item = TimeLocation(
            user_id=user_id,
            session_token=session_token,
            time=time, latitude=latitude,
            longitude=longitude,
            last_update=datetime.now(timezone.utc).timestamp()
        )
        return self.commit_db(db_item=db_item, operation_name='create_time_location_entry')

    def update_time_location_entry(self, user_id: str, session_token: str, time: str, latitude: float, longitude: float):
        """
        Updates an existing TimeLocation entry in the database. If no entry exists, creates a new one.

        Args:
            user_id (str): The user ID.
            session_token (str): The session token.
            time (str): The time of the location data.
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.
        """
        db_item = self.db.query(TimeLocation).filter(TimeLocation.user_id == user_id).first()

        if db_item:
            # If a TimeLocation entry exists, update the fields
            db_item.session_token = session_token
            db_item.time = time
            db_item.latitude = latitude
            db_item.longitude = longitude
            db_item.last_update = datetime.now(timezone.utc).timestamp()
            return self.commit_db(db_item=db_item, operation_name='update_time_location_entry')
        else:
            # If no TimeLocation entry exists for the user_id, create a new one
            return self.create_time_location_entry(user_id=user_id, session_token=session_token, time=time, latitude=latitude, longitude=longitude)

    def delete_time_location_entry(self, user_id: str):
        """
        Deletes the TimeLocation entry from the database using the user ID.

        Args:
            user_id (str): The user ID.
        """
        # Query for the entry
        db_item = self.db.query(TimeLocation).filter(TimeLocation.user_id == user_id).first()

        # If the entry exists, delete it
        if db_item:
            self.db.delete(db_item)
            return self.commit_db(db_item=db_item, operation_name='delete_time_location_entry')

    def remove_expired_allow_list_entries(self):
        """
        Iterates over all entries in the AllowList table, checks the last_update field of the related TimeLocation entry,
        and removes the user from the AllowList if the last_update is more than 5 minutes ago.
        """
        # Get the current time
        current_time = datetime.now(timezone.utc)

        # Get all entries from the AllowList table
        allow_list_entries = self.read_allow_list()

        for entry in allow_list_entries:
            # Get the related TimeLocation entry
            time_location_entry = self.db.query(TimeLocation).filter(TimeLocation.user_id == entry.user_id).first()

            if time_location_entry:
                # Calculate the time difference between the current time and the last update
                time_difference = current_time - datetime.fromtimestamp(time_location_entry.last_update, tz=timezone.utc)

                # If the last update was more than 5 minutes ago, remove the user from the AllowList
                if time_difference > timedelta(minutes=5):
                    self.delete_allow_list_entry(user_id=entry.user_id)
