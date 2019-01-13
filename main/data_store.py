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

class DataStore:
    """"Contains the data storage (in memory) of a single task"""

    def __init__(self, task_id):

        self.task_id = task_id
        self.modified = False

        # members that will be filled in by the configuration loader;
        # initialized to None for now
        self.items = None
        self.keys = None

    def __eq__(self, other):
        return self.task_id == other.task_id and self.items == other.items and \
               self.keys == other.keys

    def get_config_value(self, key):
        if key in self.keys:
            return self.keys[key]
        else:
            raise KeyError("Key '" + key + "' not found for task '" +
                           self.task_id + "'")

    def get_item_ids(self):
        return list(self.items.keys())

    def get_item_history(self, item_id):
        if item_id in self.items:
            return self.items[item_id]
        else:
            raise KeyError("Item '" + item_id + "' not found for task '" +
                           self.task_id + "'")

    def set_item_history(self, item_id, history):
        if item_id in self.items:

            # quick check that data types don't change
            if len(self.items[item_id]) > 0 and len(history) > 0:
                assert type(self.items[item_id][-1]) == type(history[-1])

            self.items[item_id] = history
            self.modified = True
        else:
            raise KeyError("Item '" + item_id + "' not found for task '" +
                           self.task_id + "'")