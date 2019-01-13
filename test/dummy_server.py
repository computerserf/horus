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

"""The mock server process

Contains the launcher for the mock server process."""

import http.server
import os
import sys

address = "127.0.0.1"
port = 8000
directory = "files"

def launch():
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer((address, port), handler)
    httpd.serve_forever()

def server_process_execute():
    os.chdir('./test/' + directory)
    launch()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server_process_execute()