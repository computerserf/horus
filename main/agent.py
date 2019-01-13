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

class Agent():
    """The software agent that fetches and processes price history"""

    def __init__(self, data_store):
        self.data_store = data_store

    def execute(self, notifier, engine):
        # get the target server
        server_address = self.data_store.get_config_value("server_url")

        # get the maximum history length
        history_length = self.data_store.get_config_value("max_history_length")

        if history_length <= 0:
            raise RuntimeError(self.data_store.task_id + ": Expected history length to be positive")

        # get the list of items
        items = self.data_store.get_item_ids()

        # for every item
        for i in range(len(items)):

            item = items[i]

            history = self.data_store.get_item_history(item)

            # fetch the latest price
            latest = engine.fetch(server_address, item)

            # if the latest price is a drop, add it to the notifier
            if engine.compare(latest, history):
                notifier.add(item, latest)

            # append the latest price to the history
            new_history = history + [latest]

            self.data_store.set_item_history(item, new_history[-history_length:])

            if i < len(items) - 1:
                engine.wait()

        # notify the user
        notifier.alert()