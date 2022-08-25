# How to use websockets with Go in App Service

> **NOTE**:
>
> - These instructions only apply to Linux app service plans
> - These instructions are for Go only

Websockets are a great tool for bi-directional messaging and can be used with App Service. In this tutorial, we will create a simple chat client/server using websockets and Node.js. The chat app is based off of the following tutorial from [elliotforbes](https://github.com/TutorialEdge/go-websockets-tutorial).

## Prerequisites

This guide uses the [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest) to configure your resources. If you don't want to install the Azure CLI locally, you can always use [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/quickstart).

This guide also assumes that you have [Go](https://go.dev/doc/install) installed locally.

## STEP 1 create a simple main.go

First, create a folder for your project and create a file called main.go. We will be doing most of our coding here.

```golang

package main

import "fmt"

func main() {
    fmt.Println("Hello World")
}

```

If you want to do a sanity check, you can run this by opening up a terminal, navigating to your project’s directory and then calling `go run main.go`. You should see that it successfully outputs `Hello World` in your terminal.

We’re going to start off by building a simple HTTP server that returns `Hello World` whenever we hit it on port 8081. We’ll also define a simple HTTP endpoint that will act as the base of the WebSocket endpoint that we’ll be creating:

```golang

package main

import (
    "fmt"
    "log"
    "net/http"
)

func homePage(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Home Page")
}

func wsEndpoint(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello World")
}

func setupRoutes() {
    http.HandleFunc("/", homePage)
    http.HandleFunc("/ws", wsEndpoint)
}

func main() {
    fmt.Println("Hello World")
    setupRoutes()
    log.Fatal(http.ListenAndServe(":8081", nil))
}

```

In order to create a WebSocket endpoint, we effectively need to upgrade an incoming connection from a standard HTTP endpoint to a long-lasting WebSocket connection. In order to do this, we are going to be using the functionality provided by the [gorilla/websocket](https://github.com/gorilla/websocket) package. You can install the package locally by running

```golang
go get github.com/gorilla/websocket

```

The first thing we’ll have to do is to define a `websocker.Upgrader` struct. This will hold information such as the Read and Write buffer size for our WebSocket connection:

```golang

// We'll need to define an Upgrader
// this will require a Read and Write buffer size
var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
}

```

The next thing we’ll want to add to our existing `wsEndpoint` function is a call to `upgrader.CheckOrigin`. This will determine whether or not an incoming request from a different domain is allowed to connect, and if it isn’t they’ll be hit with a CORS error.

```golang
func wsEndpoint(w http.ResponseWriter, r *http.Request) {
    // remove the previous fmt statement
    // fmt.Fprintf(w, "Hello World")
    upgrader.CheckOrigin = func(r *http.Request) bool { return true }

}

```

We can now start attempting to upgrade the incoming HTTP connection using the `upgrader.Upgrade()` function which will take in the Response Writer and the pointer to the HTTP Request and return us with a pointer to a WebSocket connection, or an error if it failed to upgrade.

```golang
func wsEndpoint(w http.ResponseWriter, r *http.Request) {
    upgrader.CheckOrigin = func(r *http.Request) bool { return true }

    // upgrade this connection to a WebSocket
    // connection
    ws, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        log.Println(err)
    }

}

```

Next, we’ll want to implement a function which will continually listen for any incoming messages sent through that WebSocket connection.

```golang
// define a reader which will listen for
// new messages being sent to our WebSocket
// endpoint
func reader(conn *websocket.Conn) {
    for {
        // read in a message
        messageType, p, err := conn.ReadMessage()
        if err != nil {
            log.Println(err)
            return
        }
        // print out that message for clarity
        fmt.Println(string(p))
        p = append(p, " - from the server"...)
        if err := conn.WriteMessage(messageType, p); err != nil {
            log.Println(err)
            return
        }

    }
}

```

With this defined, we can then add it to our wsEndpoint function like so:

```golang
func wsEndpoint(w http.ResponseWriter, r *http.Request) {
    upgrader.CheckOrigin = func(r *http.Request) bool { return true }

    // upgrade this connection to a WebSocket
    // connection
    ws, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        log.Println(err)
    }
    // helpful log statement to show connections
    log.Println("Client Connected")

    reader(ws)
}

```

Finally, since WebSockets allow for duplex communication, i.e. back-and-forth communication across the same TCP connection, you can send messages from your Go application to any connected Websocket clients by using the `WriteMessage` function.

The complete main.go should look like this:

```golang
package main

import (
    "fmt"
    "log"
    "net/http"

    "github.com/gorilla/websocket"
)

// We'll need to define an Upgrader
// this will require a Read and Write buffer size

var upgrader = websocket.Upgrader{
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
    CheckOrigin:     func(r *http.Request) bool { return true },
}

// define a reader which will listen for
// new messages being sent to our WebSocket
// endpoint
func reader(conn *websocket.Conn) {
    for {
    // read in a message
    messageType, p, err := conn.ReadMessage()
    if err != nil {
        log.Println(err)
        return
        }
    // print out that message for clarity
    log.Println(string(p))
    p = append(p, " - from the server"...)
    if err := conn.WriteMessage(messageType, p); err != nil {
        log.Println(err)
        return
        }

    }
}

func homePage(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Home Page")
}

func wsEndpoint(w http.ResponseWriter, r *http.Request) {
    // upgrade this connection to a WebSocket
    // connection
    ws, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        log.Println(err)
    }

    log.Println("Client Connected")
    err = ws.WriteMessage(1, []byte("Hi Client!"))
    if err != nil {
        log.Println(err)
    }
    // listen indefinitely for new messages coming
    // through on our WebSocket connection
    reader(ws)
}

func setupRoutes() {
    http.HandleFunc("/", homePage)
    http.HandleFunc("/ws", wsEndpoint)
}

func main() {
    fmt.Println("Hello World")
    setupRoutes()
    log.Fatal(http.ListenAndServe(":8081", nil))
}
```

You should be able to run this locally by typing ```go run main.go``` at the terminal.

## Step 2 create a simple index.html

Now that we have our main.go complete, we need to create an index.html file to act as a client for our websocket which should allow us to send and receive messages through the websocket. For this example, the index.html file will need to live in the same directory as the main.go file.

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

      ws = new WebSocket('ws://127.0.0.1:8081/ws');
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

To test locally, you can use a npm library called `live-server`. At the terminal, run these commands

```script
npm install -g live-server
live-server
```

This will automatically open a window in your preferred browser and serve any of the files in the current directory - in this case, our index.html. 

On another terminal window, run `go run main.go` and you should see a full duplex connection between the client and the server.

## Step 4 deploy to app service

After you're satisfied with you websockets app, you can deploy to app service using the Azure CLI.

**IMPORTANT** remember to switch your websocket URL in index.html from `ws://localhost:8080/ws` to `wss://<app-name>.azurewebsites.net/ws`. Also, in your main.go, change `log.Fatal(http.ListenAndServe(":8081", nil))` to `log.Fatal(http.ListenAndServe(":8080", nil))`. This is because the default container port on app service is 8080.

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
