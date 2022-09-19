#!/usr/bin/env python3
#
# Copyright (c) Facebook, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""See docstring for AcrolinxURLProvider class"""

from __future__ import absolute_import, division, print_function, unicode_literals

import json
from autopkglib import ProcessorError
from autopkglib.URLGetter import URLGetter



__all__ = ["AcrolinxURLProvider"]

URL = "https://{}:{}@download.acrolinx.com:1443/api/deliverables/{}/download/latest"


class AcrolinxURLProvider(URLGetter):
    """Provides a download URL for Acrolinx."""

    description = __doc__
    input_variables = {
        "acrolinx_uuid": {"required": True, "description": "UUID that seems to correspond to a specific Acrolinx customer portal"},
        "acrolinx_username": {"required": True, "description": "Username for authentication."},
        "acrolinx_password": {"required": True, "description": "Password for authentication"},
    }
    output_variables = {"url": {"description": "Download URL for Acrolinx."}}

    def main(self):
        """Find the download URL"""
        uuid = self.env["acrolinx_uuid"]
        username = self.env["acrolinx_username"]
        password = self.env["acrolinx_password"]
        if username == "username" or password == "password":
            raise ProcessorError(
                "acrolinx_username or acrolinx_password still has placeholder value"
            )
        url = URL.format(username, password, uuid)
        cmd = [self.curl_binary(), "--write-out", "'%{json}'", url]
        out, err, code = self.execute_curl(cmd)
        if code != 0:
            raise ProcessorError(
                f"{cmd} exited non-zero.\n{err}"
            )
        json_blob = out.split("{")[1]
        json_blob = "{" + json_blob # add back { so it is valid jsoin
        json_blob = json_blob.rstrip("'")
        self.output(json_blob)
        d = json.loads(json_blob)
        url = d['redirect_url']
        self.output(f"Found URL: {url}")
        self.env["url"] = url


if __name__ == "__main__":
    PROCESSOR = AcrolinxURLProvider()
    PROCESSOR.execute_shell()
