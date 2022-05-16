# How to use websockets with FastAPI in App Service

> **NOTE**:
>
> - These instructions only apply to Linux app service plans
> - These instructions are for FastAPI and Python 3.X only

Websockets are a great tool for bi-directional messaging and can be used with App Service. In this tutorial, we will create a simple chat client/server using websockets, python, and FastAPI. The chat server is based off of the example from [FastAPI](https://fastapi.tiangolo.com/advanced/websockets/) and the chat client is based on examples from [karlhadwen](https://github.com/karlhadwen/node-ws-multi-chat) and [heroku](https://github.com/heroku-examples/node-socket.io).

## Prerequisites

This guide uses the [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest) to configure your resources. If you don't want to install the Azure CLI locally, you can always use [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/quickstart).

This guide also assumes that you have [Python 3](https://www.python.org/downloads/) and pip3 installed locally. 

## Step 0.1 create a virtual environment

This guide uses virtual environments to ensure all our dependencies are isolated to this project only. To create a virtual environment, run the following command in the working directory of your project: 

```bash
python3 -m venv venv
```

This creates a virtual environment called `venv` that we'll use to isolate our dependencies. Before we do anything else though, we need to activate our virutal environment with the following command: 

```bash
source venv/bin/activate
```

Now with our virtual environment active, we can proceed to the next step. 

## Step 0.2 create requirements.txt and install dependencies

We'll use a requirements.txt file to keep track of our dependencies, which for this example, are minimal. Create a file called `requirements.txt` at the root of our application with the following contents.

```
fastapi
gunicorn
uvicorn[standard]
```

After creating this file, install the dependencies to our virtual environment by running the following command: 

```bash
pip3 install -r requirements.txt
```
## Step 1 create connection manager for websocket server

With all dependencies installed, we're ready to start building our application. To handle websocket connections and to broadcast websocket messages to all connected clients, we'll need a connection manager. Let's create this connection manager at the root of our app called `connections.py` with the following content.

```python
from typing import List
from starlette.websockets import WebSocket

class ConnectionManager():
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()
```

## Step 2 create main.py

Now that we have the ability to handle websocket connections and messages, we need to create a `main.py` at the root of our app to act as both our websocket server and to serve up the website that will act as our websocket client. 

This python source file contains functions to handle both typical GET requests by serving up the client (website) and websocket connection & message requests.

**IMPORTANT** remember to switch your websocket URL from `ws://localhost:8000/ws` to `wss://<app-name>.azurewebsites.net/ws` before deployment on App Service. The port number must **NOT** be specified upon deployment. Explicitly specifying a front-end port for this application will result in websocket timeouts since the front-end App Service port 8000 is not listening for those requests.

Also be sure to use `wss://` instead of `ws://` to avoid issues upon deployment.


```python
'''
Websockets sample for FastAPI
FastAPI handles both Websockets routes (via Starlette wrapper) and HTML responses
'''

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from connections import manager

app = FastAPI()

# FOR LOCAL TESTING ONLY
# Update websockets url to wss://<app-name>.azurewebsites.net/ws
html = """
<h1>Real Time Messaging</h1>
<pre id="messages" style="height: 400px; overflow: scroll"></pre>
<input type="text" id="messageBox" placeholder="Type your message here" style="display: block; width: 100%; margin-bottom: 10px; padding: 10px;" />
<button id="send" title="Send Message!" style="width: 100%; height: 30px;">Send Message</button>

<script>
  (function() {
    const sendBtn = document.querySelector('#send');
    const messages = document.querySelector('#messages');
    const messageBox = document.querySelector('#messageBox');

    let ws;

    function showMessage(message) {
      messages.textContent += `\n\n${message}`;
      messages.scrollTop = messages.scrollHeight;
      messageBox.value = '';
    }

    function init() {
      if (ws) {
        ws.onerror = ws.onopen = ws.onclose = null;
        ws.close();
      }

      ws = new WebSocket('ws://localhost:8000/ws');
      ws.onopen = () => {
        console.log('Connection opened!');
      }
      ws.onmessage = ({ data }) => showMessage(data);
      ws.onclose = function() {
        ws = null;
      }
      ws.onerror = function(error) {
        console.log(error);
      }
    }

    sendBtn.onclick = function() {
      if (!ws) {
        showMessage("No WebSocket connection :(");
        return ;
      }

      ws.send(messageBox.value);
    }

    init();
  })();
</script>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(websocket.url.path)
    print(websocket.url.port)
    print(websocket.url.scheme)

    await manager.connect(websocket)
    while True:
        try:
          data = await websocket.receive_text()
          await manager.broadcast({data})
        except Exception as e:
          print('error: ', e)
          break
        
```

## Step 3 test locally

Before testing, confirm that your directory structure matches the following example: 

```
<app-name>/
    venv/
    connections.py
    main.py
    requirements.txt
```

To test locally, run the follwing command from your application root: 

`gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app`

## Step 4 deploy to app service

After you're satisfied with you websockets app, you can deploy to app service using the Azure CLI. 

**IMPORTANT** remember to switch your websocket URL from `ws://localhost:8000/ws` to `wss://<app-name>.azurewebsites.net/ws`. 

To deploy your app, run the following Azure CLI commands: 

```bash
az webapp up --sku B1 --name <app-name> --resource-group <resource-group-name> --subscription <subscription-name>
az webapp config set --name <app-name> --resource-group  <resource-group-name> --startup-file "gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app"
```

The first command will create a Basic pricing tier webapp with your specified name in the resource group and subscription of your choice. The second command sets a custom startup script to use uvicorn worker(s) to kick off our FastAPI app. 

## Troubleshooting

If your application refuses to properly start or your websockets refuse to connect, first make sure your `main.py` is using `wss://<app-name>.azurewebsites.net/ws` for websocket connections. Specifying a port or using `ws://` will likely cause websocket connection timeouts or connection refusals.

## Clean up resources

When no longer needed, you can use the [az group delete](https://docs.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest#az-group-delete) command to remove the resource group, and all related resources:

```azurecli-interactive
az group delete --resource-group <resource-group-name>
```
