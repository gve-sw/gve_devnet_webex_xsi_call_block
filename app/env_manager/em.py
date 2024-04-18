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

from dotenv import load_dotenv, set_key
import os
from pathlib import Path
import typer
from app.config.config import c
from typing import ClassVar, Optional, List
from rich.console import Console

ENV_FILE_PATH = c.ENV_FILE_PATH
ENV_PATH = ENV_FILE_PATH
console = Console()


class EM:
    """
    Environment Manager class to manage environment variables and configuration.
    """
    _instance: ClassVar[Optional['EM']] = None

    def __init__(self, env_path: Path):
        """
        Initialize the Environment Manager with the path to the .env file.
        """
        self.env_path = ENV_FILE_PATH

    @classmethod
    def get_instance(cls) -> 'EM':
        """
        Returns a singleton instance of Environment Manager.
        """
        if cls._instance is None:
            cls._instance = cls(env_path=ENV_FILE_PATH)
        return cls._instance

    def create_and_load_env_if_missing(self):
        """
        Create the .env file if it doesn't exist and load the environment variables from it.
        """
        if not self.env_path.exists():
            self.env_path.touch()
        load_dotenv(dotenv_path=self.env_path)
        # console.print(f"Loaded environment variables from {self.env_path}: {os.environ}")

    def ensure_vars_set(self, var_names: List[str]):
        """
        Ensure that the specified environment variables are set and are strings.
        """
        load_dotenv(dotenv_path=self.env_path)
        for var_name in var_names:
            var_value = os.getenv(var_name)
            if var_value is None or not isinstance(var_value, str) or var_value == '':
                new_value = typer.prompt(f"Please enter a value for {var_name}")
                os.environ[var_name] = new_value
                set_key(self.env_path.as_posix(), var_name, new_value, quote_mode="never")
                load_dotenv(dotenv_path=self.env_path)
            else:
                console.print(f"{var_name} is already set.", style="bright_green")

    def ensure_settings_set(self, setting_names: List[str]):
        """
        Ensure that the specified settings are set and are of the correct type.
        """
        settings_file_path = c.SETTINGS_FILE_PATH  # Path to the settings.py file
        for setting_name in setting_names:
            setting_value = getattr(c, setting_name, None)
            if setting_value is None or (setting_name == 'GEOLOCATION_TIMEOUT' and not isinstance(setting_value, int)) or (
                    setting_name != 'GEOLOCATION_TIMEOUT' and not isinstance(setting_value, float)):
                while True:  # Loop until the user enters a valid value
                    new_value = typer.prompt(f"Please enter a value for {setting_name}")
                    try:
                        # Attempt to convert the user input to the correct type
                        if setting_name == 'GEOLOCATION_TIMEOUT':
                            new_value = int(new_value)
                        else:
                            new_value = float(new_value)
                        break  # If the conversion is successful, break the loop
                    except ValueError:
                        console.print(f"Invalid value. Please enter a {'integer' if setting_name == 'GEOLOCATION_TIMEOUT' else 'float'} for {setting_name}.",
                                      style="bright_red")
                # Read the settings.py file
                with open(settings_file_path, 'r') as file:
                    lines = file.readlines()
                # Replace the line that contains the setting
                for i, line in enumerate(lines):
                    if line.startswith(setting_name):
                        lines[i] = f"{setting_name}: {type(new_value).__name__} = {new_value}\n"
                        break
                # Write the changes back to the settings.py file
                with open(settings_file_path, 'w') as file:
                    file.writelines(lines)
            else:

                console.print(f"{setting_name} is already set.", style="bright_green")


em = EM.get_instance()
