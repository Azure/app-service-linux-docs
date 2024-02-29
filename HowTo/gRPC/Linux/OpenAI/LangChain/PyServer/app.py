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
"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures
# import logging

# must enable SCM_DO_BUILD_DURING_DEPLOYMENT=true
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

from flask import Flask
# import time

from langchain import OpenAI
# import openai

app = Flask(__name__)

@app.route('/')
def func():
    return "Grpc Server w/ OpenAI API"

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        llm = OpenAI(openai_api_key="[YOUR-API-KEY]")
        text = llm.predict(request.name)
        return helloworld_pb2.HelloReply(message=text)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    app.logger.info("adding insecure port 8282")
    p = server.add_insecure_port('0.0.0.0:8282')
    app.logger.info("opened up on port ")
    app.logger.info(p)
    server.start()
    return server

if __name__ == '__main__':
    app.logger.info("starting up")
    grpc_server = serve()
    app.logger.info("serving grpc")
    app.run(host="0.0.0.0", port=8000)
    