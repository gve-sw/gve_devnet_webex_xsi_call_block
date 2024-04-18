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

from rich.console import Console
from rich.pretty import Pretty
from rich.table import Table
from rich.panel import Panel
import logging
import logging.handlers
import queue
from rich.logging import RichHandler
from logging.handlers import TimedRotatingFileHandler
from rich import inspect
from threading import Lock
import os
from .custom_themes import ct


class LoggerManager:
    """
    Logger Manager class to manage logging and console output.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LoggerManager, cls).__new__(cls)
            return cls._instance

    def __init__(self):
        self.listener = None
        self.console = Console(theme=ct)  # Uses custom themes Class
        self.log_queue = queue.Queue(-1)  # No limit on size
        self.queue_handler = logging.handlers.QueueHandler(self.log_queue)
        self.log_dir = "logger/logs"
        self.log_file = self.log_dir + "/app.log"
        self.logger = self.setup()
        self.original_log_level = self.logger.level
        self.session_logs = {}  # This will store all the logs per session
        self.logger.propagate = False
        self.lock = Lock()

    def setup(self):
        """Set up the logger with handlers for both console and file output."""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        log_directory = self.log_dir  # Create the log directory if it doesn't exist
        if not os.path.exists(log_directory):  # Create the log directory if it doesn't exist
            os.makedirs(log_directory)  # Create the log directory if it doesn't exist

        file_handler = logging.FileHandler(self.log_file)  # Create a file handler

        # Set up a TimedRotatingFileHandler
        # file_handler = TimedRotatingFileHandler(
        #     filename=self.log_file,  # Set the log file name
        #     when="D",  # Rotate daily
        #     backupCount=28,  # Keep 28 days of logs
        #     encoding='utf-8',   # Set the encoding
        #     delay=False     # Do not delay the file creation
        # )
        file_handler.setLevel(logging.DEBUG)  # Set the file handler level to DEBUG
        file_handler.setFormatter(logging.Formatter(log_format))  # Set the file handler format

        console_handler = RichHandler(console=self.console, rich_tracebacks=True)  # Create a console handler
        console_handler.setLevel(logging.DEBUG)  # Set the console handler level to DEBUG

        logger = logging.getLogger(__name__)  # Get the logger
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)  # Add the file handler to the logger
        logger.propagate = False

        self.listener = logging.handlers.QueueListener(
            self.log_queue, console_handler, file_handler, respect_handler_level=True
        )
        self.listener.start()  # Start the listener
        return logger  # Return the logger

    def tsp(self, *args, **kwargs):
        """Thread safe print."""
        with self.lock:  # Use the lock to ensure thread safety
            self.console.print(*args, **kwargs)  # Print the args

    def pp(self, *args, style="info", level="info"):
        """Pretty printing with thread safe print."""
        # Check if there are arguments to print
        if args:
            pretty_args = Pretty(args)  # Format the args using Pretty
            self.tsp(pretty_args)  # Print the pretty-formatted args
            # Convert the args to a single string for logging
            message = ' '.join(map(str, args))
            self.lnp(message, style=style, level=level)  # Log the message

    def lnp(self, message, style="info", level="info", **kwargs):
        """ Log n' print the message
        Log the message at the given level and print it to the console with the given style."""
        level_method = getattr(self.logger,  # Get the method from the logger
                               level.lower(),  # Convert the level to lowercase
                               self.logger.info  # Default to info if the level is not found
                               )
        level_method(message, **kwargs)  # Log the message
        self.tsp(message, style=style, **kwargs)  # Print the message

    def p_panel(self, *args, **kwargs):
        """Create and print a Rich Panel in a thread-safe manner."""
        panel = Panel(*args, **kwargs)  # Create a Rich Panel
        self.lnp(panel) # Log and print the panel

    def lnp_wbx_oauth(self, message: str, style: str = 'webex', expand: bool = False):
        """
        Wrap a message with a specific style for Webex Oauth messages and print it to the console with a Rich Panel.
        """
        lm.p_panel(f'[bright_white]{message}[/bright_white]', style=style, expand=expand)

    def print_2_column_rich_table(self, data, title: str = "Table Name"):
        """
        Display data in a rich table format.
        """
        table = Table(title=title)
        table.add_column("Variable", justify="left", style="bright_white", width=30)
        table.add_column("Value", style="bright_white", width=60)

        for var_name, var_value in data:
            table.add_row(var_name, str(var_value) if var_value not in [None, ""] else "Not Set")
        self.tsp(table)

    def print_config_table(self, config_instance: object):
        config_data = [(name, value) for name, value in config_instance.env_vars.items()]
        self.print_2_column_rich_table(data=config_data, title="Environment Variables & Settings")

    def display_list_as_rich_table(self, data_list, title, headers=None):
        """Display a list of dictionaries in a rich table format."""
        if not data_list or not all(isinstance(item, dict) for item in data_list):
            self.tsp("Invalid data provided for the table.")
            return

        headers = headers or data_list[0].keys()
        table = Table(title=title)
        for header in headers:
            table.add_column(header, style="bright_white")

        self._add_rows_to_table(table, data_list, headers)
        self.tsp(table)

    def print_start_panel(self, app_name=""):
        self.lnp(Panel.fit(f'[bold bright_white]{app_name}[/bold bright_white]', title='Start', style='webex'))

    def print_exit_panel(self):
        self.lnp("\n")
        self.lnp(Panel.fit('Shutting down...', title='[bright_red]Exit[/bright_red]', border_style='red'))

    def debug_inspect(self, obj):
        """
        Inspect an object using Rich and log the representation.
        """
        inspect(obj, console=self.console, methods=True)
        self.tsp(f"Inspected object: {type(obj).__name__}")

    def exception(self, message, extra_data=None):
        """Log an exception along with a custom message."""
        if extra_data:
            message += f' - Extra data: {extra_data}'
        self.logger.exception(message)

    def print_admin_start_panel(self, public_url: str):
        self.p_panel(
            f'[bright_white]Hello Admin. Please login here to proceed: {public_url}/admin/login[/bright_white]',
            style="orange1",
            expand=False
        )

    def print_xsi_user_map(self, xsi_user_map):
        # Convert the xsi_user_map dictionary to a list of dictionaries
        data_list = [value for value in xsi_user_map.values()]

        # Print the data in a table format
        self.display_list_as_rich_table(data_list, title="XSI User Map")

    def _add_rows_to_table(self, table, data_list, headers):
        """Helper method to add rows to a table."""
        for item in data_list:
            row = [str(item.get(header, '')) for header in headers]
            table.add_row(*row)


lm = LoggerManager()
