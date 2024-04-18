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

import requests
import json
from logger.logrr import lm
from config.config import c


class MyWebex:
    """
    MyWebex class to handle interactions with Webex APIs.
    """

    def __init__(self, access_token):
        """
        Initialize MyWebex with the given access token.
        Args:
            access_token (str): Webex API access token.
            webex_room_id (str, optional): ID of the Webex room to send messages to.
        """
        self.base_url = c.WEBEX_BASE_URL
        self.access_token = access_token
        self.headers = {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}

    def webex_api_call(self, method, endpoint, data=None):
        """
        Generic function to make API calls to Webex.
        Args:
            method (str): HTTP method ('get', 'post', 'delete', etc.).
            endpoint (str): API endpoint url.
            data (dict, optional): Payload for POST requests.
        Returns:
            Response object: The response from the Webex API.
        """
        url = f'{self.base_url}/{endpoint}'
        # lm.p_panel(f"url: {url}, headers: {self.headers}, endpoint: {endpoint}")  # debugging
        response = requests.request(method, url, headers=self.headers, json=data)
        self.handle_response(response)
        return response

    def handle_response(self, response):
        status_code_messages = {
            200: '[bright_green]200: Webex Call Successful - Data retrieved or successfully modified[/bright_green]',
            201: '[bright_green]201: Webex API Call Successful - Data retrieved or successfully modified[/bright_green]',
            202: '[bright_green]202: Webex API Call Successful - Request accepted and processing (asynchronous operation)[/bright_green]',
            203: '[bright_green]203: Webex API Call Successful - Request successful, no content to return[/bright_green]',
            204: '[bright_green]204: Webex API Call Successful - Request successful, no content to return[/bright_green]',
            400: '[red]400: Bad Request - The request was invalid or cannot be otherwise served[/red]',
            401: '[red]401: Unauthorized - Authentication credentials were missing or incorrect[/red]',
            403: '[red]403: Forbidden - The request is understood, but it has been refused or access is not allowed[/red]',
            404: '[red]404: Not Found - The URI requested is invalid or the resource requested does not exist[/red]',
            500: '[red]500: Internal Server Error - Something is broken on the server[/red]',
            503: '[red]503: Service Unavailable - The server is currently unable to handle the request due to a temporary overload or maintenance[/red]'
        }

        # Print the corresponding message for the status code
        lm.console.print(
            status_code_messages.get(response.status_code, f'Error handling Webex API call. Status Code: {response.status_code}. Response: {response.text}'))

        # Handle JSON content if the response is successful
        if response.status_code in [200, 201, 202, 203, 204]:
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text  # For responses without JSON content

    def check_token_validity(self):
        """
        Check if the provided Webex access token is valid.
        Returns:
            bool: True if the token is valid, False otherwise.
        """
        response = self.webex_api_call('get', 'people/me')
        if response.status_code == 200:
            return True
        else:
            lm.logger.error(f'Invalid or expired token. Response: {response.text}')
            return False

    def get_user_info(self):
        """
        Fetches the user's information from the Webex API.
        Returns:
            dict: User information.
        """
        endpoint = 'people/me'
        response = self.webex_api_call('GET', endpoint)
        return self.handle_response(response)

    def get_person_details(self, person_id):
        endpoint = f'people/{person_id}'
        response = self.webex_api_call('GET', endpoint)
        return self.handle_response(response)
