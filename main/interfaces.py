#     Copyright 2018-2019 Haresh Bhagchandani
#
#     This file is part of Horus.
#
#     Horus is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Horus is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Horus.  If not, see <https://www.gnu.org/licenses/>.

class Notifier():
    """The notifier interface

    This interface is used by the agent to build a notification message
    incrementally and alert the user."""

    def __init__(self):
        pass

    def add(self, item_id, latest_data_point):
        """Function called whenever Engine.compare() returns true when examining
        an item's latest data point in order to incrementally build an alert message.

        item_id (string) - the identifier of the item whose data point passes the comparison,
                            as given in the configuration file

        latest_data_point (object) - the latest data point"""
        raise NotImplementedError

    def alert(self):
        """Function called after all items have been examined to notify the user"""
        raise NotImplementedError

class Engine():
    """The engine interface

    This interface is used by the agent to fetch prices, compare the latest
    prices, and even to wait between requests"""

    def __init__(self):
        pass

    def fetch(self, server_url, item_id):
        """Function called to fetch the latest item data point from a server

        server_url (string) - the url of the resource to get, as given in
                              the configuration file

        item_id (object) - the identifier of the item whose data point passes
                           the comparison,as given in the configuration file

        Returns the latest data point"""
        raise NotImplementedError

    def compare(self, latest_data_point, history):
        """Function called to compare the latest data point of an item to its history

        latest_data_point (object) - the latest data point

        history (list(object)) - the known history of item's data points, from oldest
                                 to newest

        Returns True if the user should be notified of the latest data point"""
        raise NotImplementedError

    def wait(self):
        """Function called between each item fetched from a url, for things such as
        waiting between requests"""
        raise NotImplementedError
