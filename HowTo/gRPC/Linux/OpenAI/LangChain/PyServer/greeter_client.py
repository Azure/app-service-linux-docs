# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function

import logging

import grpc
import helloworld_pb2
import helloworld_pb2_grpc


def run():
    creds = grpc.ssl_channel_credentials()
    # replace localhost:8282 with [APP_NAME].azurewebsites.net
    # DO NOT include a port number with your app service URL (.azurewebsites.net by default)
    # DON'T FORGET to change the insecure channel to a secure channel before deploying to App Service
 
    while True:
        with grpc.insecure_channel('localhost:8282') as channel:
        # with grpc.secure_channel('[APP-NAME].azurewebsites.net', creds) as channel:   
            stub = helloworld_pb2_grpc.GreeterStub(channel)
            text = input("Enter query request to gRPC server (Press ENTER to quit):")
            response = stub.SayHello(helloworld_pb2.HelloRequest(name=text))
            print(response.message)
            if text == " ":
                break

if __name__ == '__main__':
    logging.basicConfig()
    run()
