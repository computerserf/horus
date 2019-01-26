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

import json
import collections

from main.data_store import DataStore
from main.agent import Agent
from main.interfaces import Engine, Notifier

######################### CONFIGURE THE CODE BELOW #########################

# Put you Notifier and Engine object definitions here

def deserializer(task_id, data):
    """Deserializes a data string

    task_id (string) - the task identifier that we deserialize data from
    data (string) - the string to deserialize the data from

    Returns the data object type"""
    # if task_id == "YOUR_TASK":
    #     return YourType(data)
    raise RuntimeError("Task name not recognized")


def serializer(task_id, data):
    """Serializes a data object

    task_id (string) - the task identifier that we serialize data to
    data (object) - the object to deserialize the data from

    Returns the data object type"""
    # if task_id == "YOUR_TASK":
    #     return str(data)
    raise RuntimeError("Task name not recognized")

def find_notifier(task_id):
    """Returns a Notifier object associated with the a task

    task_id (string) - The identifier associated wit the tsk (as in config.json)

    Returns a Notifier object associated with the task"""
    # if task_id == "YOUR_TASK":
    #     return YourNotifier()
    # else:
    raise RuntimeError("Task name not recognized")


def find_engine(task_id):
    """Returns an Engine object associated with the a task

    tasl_id (string) - The identifier associated wit the tsk (as in config.json)

    Returns an Engine object associated to help process task"""
    # if task_id == "YOUR_TASK":
    #     return YourEngine()
    # else:
    raise RuntimeError("Task name not recognized")

######################### DO NOT CONFIGURE THE CODE BELOW #########################

def load_config(config_filename, data_deserializer):
    """Loads the data store for each task

    config_filename (string) - the path to the configuration file

    data_deserializer (function(string, string)) - a function that
        deserializes data strings for each task

    Returns a list of data stores"""
    # desrialize json as ordered dictionaries (need in python version < 3.7j)
    json_data = None
    with open(config_filename, "r") as fp:
        json_data = json.load(fp, object_pairs_hook = collections.OrderedDict)

    stores = []

    for task in json_data:

        ds = DataStore(task)

        ds.keys = collections.OrderedDict()
        ds.items = collections.OrderedDict()

        col = json_data[task]
        for key in col:
            if key == "items":
                item_pair = json_data[task][key]
                for item in item_pair:
                    ds.items[item] = [data_deserializer(task, k) \
                                      for k in json_data[task][key][item]]
            else:
                ds.keys[key] = json_data[task][key]

        stores.append(ds)

    return stores

def save_config(data_stores, config_filename, data_serializer):
    """Saves the data stores into a configuration file

    data_store (list(DataStore)) - The ordered list (by task) of data stores

    config_filename (string) - The path to where the  configuration should by saved

    data_serializer (function(string, object)) - a function that serializes a tasks
        data point"""
    json_data = collections.OrderedDict()

    for ds in data_stores:

        serialized_items = collections.OrderedDict()
        for i in ds.items:
            serialized_items[i] = [data_serializer(ds.task_id, k) for k in ds.items[i]]

        task = collections.OrderedDict()

        for k in ds.keys:
            task[k] = ds.keys[k]

        task["items"] = serialized_items

        json_data[ds.task_id] = task

    with open(config_filename, "w") as fp:
        json.dump(json_data, fp, indent=4)

def exec():
    data_stores = load_config("config.json", deserializer)

    for ds in data_stores:
        notifier = find_notifier(ds.task_id)
        engine = find_engine(ds.task_id)
        agent = Agent(ds)
        agent.execute(notifier, engine)

    save_config(data_stores, "config.json", serializer)

if __name__ == "__main__":
    exec()