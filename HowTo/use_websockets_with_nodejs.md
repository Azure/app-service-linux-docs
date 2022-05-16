# How to use websockets with Node.js in App Service

> **NOTE**:
>
> - These instructions only apply to Linux app service plans
> - These instructions are for Node.js only

Websockets are a great tool for bi-directional messaging and can be used with App Service. In this tutorial, we will create a simple chat client/server using websockets and Node.js. The chat app is based off of the following two tutorials from [karlhadwen](https://github.com/karlhadwen/node-ws-multi-chat) and [heroku](https://github.com/heroku-examples/node-socket.io).

## Prerequisites

This guide uses the [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest) to configure your resources. If you don't want to install the Azure CLI locally, you can always use [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/quickstart).

This guide also assumes that you have [Node.js](https://nodejs.org/en/download/) installed locally. 

## STEP 1 create a simple server.js

First, let's make a simple file named server.js that will start up our webserver and websocket server. To do this, we'll need to use the Express and WebSocket (ws) libraries. 

```javascript

const express = require('express');
const WebSocket = require('ws');

```

Then we'll need to set the port to listen on (ex: 8080), and the file to serve as our index (in this case index.html).

```javascript

const port = 8080;
const index = './index.html'

```

Next we should create a webserver using Express to serve up our index and listen on our selected port.

```javascript

const server = express()
  .use((req, res) => res.sendFile(index, { root: __dirname }))
  .listen(port, () => console.log(`Listening on port ${port}`));

```

Then we can create a websocket server using the same configuration as our Express webserver. 
The second block of code handles incoming websocket connections by allowing clients to send data (messages) if the client is ready and the websocket is open.

```javascript
const wss = new WebSocket.Server({ server })


wss.on('connection', function connection(ws) {
  ws.on('message', function incoming(data) {
    wss.clients.forEach(function each(client) {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(data);
      }
    })
  })
})

```

The complete server.js should look like this:

```javascript
const express = require('express');
const WebSocket = require('ws');

const port = 8080;
const index = './index.html'

const server = express()
  .use((req, res) => res.sendFile(index, { root: __dirname }))
  .listen(port, () => console.log(`Listening on port ${port}`));

const wss = new WebSocket.Server({ server })


wss.on('connection', function connection(ws) {
  ws.on('message', function incoming(data) {
    wss.clients.forEach(function each(client) {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(data);
      }
    })
  })
})
```

## Step 2 create a simple index.html

Now that we have our server.js complete, we need to create an index.html file to act as a client for our websocket which should allow us to send and receive messages through the websocket. For this example, the index.html file will need to live in the same directory as the server.js file.

First, let's add some static html content to facilitate the sending and receiving of messages through our websocket server.

```html
<h1>Real Time Messaging</h1>
<pre id="messages" style="height: 400px; overflow: scroll"></pre>
<input type="text" id="messageBox" placeholder="Type your message here" style="display: block; width: 100%; margin-bottom: 10px; padding: 10px;" />
<button id="send" title="Send Message!" style="width: 100%; height: 30px;">Send Message</button>
```

Then we'll need to add a script to handle the sending and receiving of messages using our websocket defined in server.js. 

Let's start by opening a script tag and defining our constants within a function. 

```html
<script>
  (function() {
    const sendBtn = document.querySelector('#send');
    const messages = document.querySelector('#messages');
    const messageBox = document.querySelector('#messageBox');

    let ws;
```

Then we can define another function to add the text of a message to our previously defined messages constant.

```javascript
    function showMessage(message) {
      messages.textContent += `\n\n${message}`;
      messages.scrollTop = messages.scrollHeight;
      messageBox.value = '';
    }
```

Next we should define a function called init() which will initialize our connection to the websocket. This function begins by checking to ensure there is no currently open/running websocket for the client before attempting to open a websocket and call the showMessage() function to display any messages received. 

Also remember to change your websocket address from localhost:8080 to your app service URL before deployment and to always use `wss://` instead of `ws://` with app service. Only encrypted websocket connections are allowed.

```javascript
    function init() {
      if (ws) {
        ws.onerror = ws.onopen = ws.onclose = null;
        ws.close();
      }

      // for local testing ONLY, change this to wss://<app-name>.azurewebsites.net before deployment or your custom domain name
      ws = new WebSocket('ws://localhost:8080');
      ws.onopen = () => {
        console.log('Connection opened!');
      }
      ws.onmessage = ({ data }) => showMessage(data);
      ws.onclose = function() {
        ws = null;
      }
    }
```

Lastly, we need to some behavior to our button to allow it to send a message through our websocket connection. The client should print the message as typed in the text box, but if the websocket cannot connect, it will print `No WebSocket connection :(`. Also, don't forget to call the init() function before closing out our outer function and script tag.

```javascript
    sendBtn.onclick = function() {
      if (!ws) {
        showMessage("No WebSocket connection :(");
        return ;
      }

      ws.send(messageBox.value);
      showMessage(messageBox.value);
    }

    init();
  })();
  </script>
```

The full index.html should look like this:

```html
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

      ws = new WebSocket('ws://localhost:8080');
      ws.onopen = () => {
        console.log('Connection opened!');
      }
      ws.onmessage = ({ data }) => showMessage(data);
      ws.onclose = function() {
        ws = null;
      }
    }

    sendBtn.onclick = function() {
      if (!ws) {
        showMessage("No WebSocket connection :(");
        return ;
      }

      ws.send(messageBox.value);
      showMessage(messageBox.value);
    }

    init();
  })();
</script>

```

## Step 3 test locally

To test locally, you'll first need to install some dependencies. Copy the following into a file called package.json before typing `npm install` into your terminal from your working directory. This should install all the necessary dependencies for this app.

```json
{
  "name": "rtm",
  "version": "0.0.1",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.17.1",
    "ws": "^7.2.3"
  }
}
```

After a successful install, type `npm start` into your terminal to test the app. You should be able to browse to http://localhost:8080 to view your app. Try opening the app in multiple browser windows and sending messages. The messages sent by any client (browser window in this case) should appear on all open clients.

## Step 4 deploy to app service

After you're satisfied with you websockets app, you can deploy to app service using the Azure CLI. 

**IMPORTANT** remember to switch your websocket URL from `ws://localhost:8080` to `wss://<app-name>.azurewebsites.net`. 

To deploy your app, run the following Azure CLI command: 

```bash
az webapp up --sku B1 --name <app-name> --resource-group <resource-group-name> --subscription <subscription-name>
```

This command will create a Basic pricing tier webapp with your specified name in the resource group and subscription of your choice. 

## Clean up resources

When no longer needed, you can use the [az group delete](https://docs.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest#az-group-delete) command to remove the resource group, and all related resources:

```azurecli-interactive
az group delete --resource-group <resource-group-name>
```
