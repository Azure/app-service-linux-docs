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
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    creds = grpc.ssl_channel_credentials()
    # DO NOT include a port number with your app service URL (.azurewebsites.net by default)
    # To use with App Service, REPLACE below line with the following: with grpc.secure_channel('[APP_NAME].azurewebsites.net', creds) as channel:
    with grpc.insecure_channel('localhost:8282') as channel:   
        print("created channel")
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        print("created stub")
        response = stub.SayHello(helloworld_pb2.HelloRequest(name='you'))
        print("response returned")
    print("Greeter client received: " + response.message)


if __name__ == '__main__':
    logging.basicConfig()
    run()
