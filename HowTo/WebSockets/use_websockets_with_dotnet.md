# How to use websockets with .Net in App Service (Windows)

> **NOTE**:
>
> - These instructions apply to both Windows and Linux App Service Plans (See Step 7)
> - These instructions are for .Net (6) only

Websockets are a great tool for bi-directional messaging and can be used with App Service. In this tutorial, we will create a simple chat client/server using websockets and Node.js. The chat app is based off of the following sample code from [AspNetCore.Docs](https://github.com/dotnet/AspNetCore.Docs/tree/main/aspnetcore/fundamentals/websockets/samples/6.x/WebSocketsSample).

## Prerequisites

This guide uses the [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest) to configure your resources. If you don't want to install the Azure CLI locally, you can always use [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/quickstart) or the Azure Portal.

This guide also assumes that you have [.Net 6](https://dotnet.microsoft.com/en-us/download/dotnet/6.0) installed locally. 

## STEP 0 create a new .NET project

Before starting, you'll need a .NET webapp. You can create one by using Visual Studio or by using the following .NET CLI command:

```bash
dotnet new webapp -f net6.0
```

## STEP 1 create a simple index.html in the wwwroot directory of your .NET app

First, let's create an index.html that will act as our websocket client. 

This allows us to open a websocket and send messages through it on the client (browser) side. These messages will be echoed by the websocket server that we will create later to handle these websocket connections and messages.

```html

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title></title>
    <style>
        table {
            border: 0
        }

        .commslog-data {
            font-family: Consolas, Courier New, Courier, monospace;
        }

        .commslog-server {
            background-color: red;
            color: white
        }

        .commslog-client {
            background-color: green;
            color: white
        }
    </style>
</head>
<body>
    <h1>WebSocket Sample Application</h1>
    <p id="stateLabel">Ready to connect...</p>
    <div>
        <label for="connectionUrl">WebSocket Server URL:</label>
        <input id="connectionUrl" />
        <button id="connectButton" type="submit">Connect</button>
    </div>
    <p></p>
    <div>
        <label for="sendMessage">Message to send:</label>
        <input id="sendMessage" disabled />
        <button id="sendButton" type="submit" disabled>Send</button>
        <button id="closeButton" disabled>Close Socket</button>
    </div>

    <h2>Communication Log</h2>
    <table style="width: 800px">
        <thead>
            <tr>
                <td style="width: 100px">From</td>
                <td style="width: 100px">To</td>
                <td>Data</td>
            </tr>
        </thead>
        <tbody id="commsLog">
        </tbody>
    </table>

    <script>
        var connectionUrl = document.getElementById("connectionUrl");
        var connectButton = document.getElementById("connectButton");
        var stateLabel = document.getElementById("stateLabel");
        var sendMessage = document.getElementById("sendMessage");
        var sendButton = document.getElementById("sendButton");
        var commsLog = document.getElementById("commsLog");
        var closeButton = document.getElementById("closeButton");
        var socket;

        var scheme = document.location.protocol === "https:" ? "wss" : "ws";
        var port = document.location.port ? (":" + document.location.port) : "";

        connectionUrl.value = scheme + "://" + document.location.hostname + port + "/ws" ;

        function updateState() {
            function disable() {
                sendMessage.disabled = true;
                sendButton.disabled = true;
                closeButton.disabled = true;
            }
            function enable() {
                sendMessage.disabled = false;
                sendButton.disabled = false;
                closeButton.disabled = false;
            }

            connectionUrl.disabled = true;
            connectButton.disabled = true;

            if (!socket) {
                disable();
            } else {
                switch (socket.readyState) {
                    case WebSocket.CLOSED:
                        stateLabel.innerHTML = "Closed";
                        disable();
                        connectionUrl.disabled = false;
                        connectButton.disabled = false;
                        break;
                    case WebSocket.CLOSING:
                        stateLabel.innerHTML = "Closing...";
                        disable();
                        break;
                    case WebSocket.CONNECTING:
                        stateLabel.innerHTML = "Connecting...";
                        disable();
                        break;
                    case WebSocket.OPEN:
                        stateLabel.innerHTML = "Open";
                        enable();
                        break;
                    default:
                        stateLabel.innerHTML = "Unknown WebSocket State: " + htmlEscape(socket.readyState);
                        disable();
                        break;
                }
            }
        }

        closeButton.onclick = function () {
            if (!socket || socket.readyState !== WebSocket.OPEN) {
                alert("socket not connected");
            }
            socket.close(1000, "Closing from client");
        };

        sendButton.onclick = function () {
            if (!socket || socket.readyState !== WebSocket.OPEN) {
                alert("socket not connected");
            }
            var data = sendMessage.value;
            socket.send(data);
            commsLog.innerHTML += '<tr>' +
                '<td class="commslog-client">Client</td>' +
                '<td class="commslog-server">Server</td>' +
                '<td class="commslog-data">' + htmlEscape(data) + '</td></tr>';
        };

        connectButton.onclick = function() {
            stateLabel.innerHTML = "Connecting";
            socket = new WebSocket(connectionUrl.value);
            socket.onopen = function (event) {
                updateState();
                commsLog.innerHTML += '<tr>' +
                    '<td colspan="3" class="commslog-data">Connection opened</td>' +
                '</tr>';
            };
            socket.onclose = function (event) {
                updateState();
                commsLog.innerHTML += '<tr>' +
                    '<td colspan="3" class="commslog-data">Connection closed. Code: ' + htmlEscape(event.code) + '. Reason: ' + htmlEscape(event.reason) + '</td>' +
                '</tr>';
            };
            socket.onerror = updateState;
            socket.onmessage = function (event) {
                commsLog.innerHTML += '<tr>' +
                    '<td class="commslog-server">Server</td>' +
                    '<td class="commslog-client">Client</td>' +
                    '<td class="commslog-data">' + htmlEscape(event.data) + '</td></tr>';
            };
        };

        function htmlEscape(str) {
            return str.toString()
                .replace(/&/g, '&amp;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
        }
    </script>
</body>
</html>

```

## Step 2 create a WebSocketController.cs class in the root directory of your .NET app

After creating an index.html to act as our websocket client, we need to create a websocket controller class as a subclass of the ControllerBase class to start handling those websocket connections and messages. 

This class contains two async tasks that will allow our websocket server to "Echo" the messages from the client.

```csharp
using System.Net.WebSockets;
using Microsoft.AspNetCore.Mvc;


// <snippet>
public class WebSocketController : ControllerBase
{
    [HttpGet("/ws")]
    public async Task Get()
    {
        if (HttpContext.WebSockets.IsWebSocketRequest)
        {
            using var webSocket = await HttpContext.WebSockets.AcceptWebSocketAsync();
            await Echo(webSocket);
        }
        else
        {
            HttpContext.Response.StatusCode = StatusCodes.Status400BadRequest;
        }
    }
    // </snippet>

    private static async Task Echo(WebSocket webSocket)
    {
        var buffer = new byte[1024 * 4];
        var receiveResult = await webSocket.ReceiveAsync(
            new ArraySegment<byte>(buffer), CancellationToken.None);

        while (!receiveResult.CloseStatus.HasValue)
        {
            await webSocket.SendAsync(
                new ArraySegment<byte>(buffer, 0, receiveResult.Count),
                receiveResult.MessageType,
                receiveResult.EndOfMessage,
                CancellationToken.None);

            receiveResult = await webSocket.ReceiveAsync(
                new ArraySegment<byte>(buffer), CancellationToken.None);
        }

        await webSocket.CloseAsync(
            receiveResult.CloseStatus.Value,
            receiveResult.CloseStatusDescription,
            CancellationToken.None);
    }
}

```

## Step 3 create a BackgroundSocketProcessor.cs internal class in the root directory of your .NET app

This is a super short class definition that allows us to add websocket connections to a collection of background threads / processes. See the following [Websocket Lifetime Guidance](https://github.com/dotnet/AspNetCore.Docs/issues/5466#:~:text=AddSocket%20%28socket%29%3B%20%7D%29%3B%20BackgroundSocketProcessor%20is%20some%20service%20or,are%20then%20accessing%20those%20sockets%20and%20sending%20data.) for more info.


```csharp
using System.Net.WebSockets;

internal class BackgroundSocketProcessor
{
    internal static void AddSocket(WebSocket webSocket, TaskCompletionSource<object> socketFinishedTcs) { }
}

```

## Step 4 create a Startup.cs class in the root directory of your .NET app

Now we need to define our Startup.cs. This class contains the methods necessary to allow our app to properly connect to and use websockets.

```csharp
using System.Net.WebSockets;


public static class Startup
{
    public static void UseWebSockets(WebApplication app)
    {
        // <snippet_UseWebSockets>
        app.UseWebSockets();
        // </snippet_UseWebSockets>
    }

    public static void AcceptWebSocketAsync(WebApplication app)
    {
        // <snippet_AcceptWebSocketAsync>
        app.Use(async (context, next) =>
        {
            if (context.Request.Path == "/ws")
            {
                if (context.WebSockets.IsWebSocketRequest)
                {
                    using var webSocket = await context.WebSockets.AcceptWebSocketAsync();
                    await Echo(webSocket);
                }
                else
                {
                    context.Response.StatusCode = StatusCodes.Status400BadRequest;
                }
            }
            else
            {
                await next(context);
            }

        });
        // </snippet_AcceptWebSocketAsync>
    }

    public static void AcceptWebSocketAsyncBackgroundSocketProcessor(WebApplication app)
    {
        // <snippet_AcceptWebSocketAsyncBackgroundSocketProcessor>
        app.Run(async (context) =>
        {
            using var webSocket = await context.WebSockets.AcceptWebSocketAsync();
            var socketFinishedTcs = new TaskCompletionSource<object>();

            BackgroundSocketProcessor.AddSocket(webSocket, socketFinishedTcs);

            await socketFinishedTcs.Task;
        });
        // </snippet_AcceptWebSocketAsyncBackgroundSocketProcessor>
    }

    public static void UseWebSocketsOptionsAllowedOrigins(WebApplication app)
    {
        // <snippet_UseWebSocketsOptionsAllowedOrigins>
        var webSocketOptions = new WebSocketOptions
        {
            KeepAliveInterval = TimeSpan.FromMinutes(2)
        };

        webSocketOptions.AllowedOrigins.Add("https://client.com");
        webSocketOptions.AllowedOrigins.Add("https://www.client.com");

        app.UseWebSockets(webSocketOptions);
        // </snippet_UseWebSocketsOptionsAllowedOrigins>
    }

    // <snippet_Echo>
    private static async Task Echo(WebSocket webSocket)
    {
        var buffer = new byte[1024 * 4];
        var receiveResult = await webSocket.ReceiveAsync(
            new ArraySegment<byte>(buffer), CancellationToken.None);

        while (!receiveResult.CloseStatus.HasValue)
        {
            await webSocket.SendAsync(
                new ArraySegment<byte>(buffer, 0, receiveResult.Count),
                receiveResult.MessageType,
                receiveResult.EndOfMessage,
                CancellationToken.None);

            receiveResult = await webSocket.ReceiveAsync(
                new ArraySegment<byte>(buffer), CancellationToken.None);
        }

        await webSocket.CloseAsync(
            receiveResult.CloseStatus.Value,
            receiveResult.CloseStatusDescription,
            CancellationToken.None);
    }
    // </snippet_Echo>
}

```

## Step 5 create / update Program.cs in the root directory of your .NET app

To kick off our .NET app, we need a main method that uses our previously defined classes to setup our websockets and serve our index.html (websocket client) to the browser.

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Hosting;


    public class Program
    {
        public static void Main(string[] args)
        {
        var builder = WebApplication.CreateBuilder(args);

        builder.Services.AddControllers();

        var app = builder.Build();

        // <snippet_UseWebSockets>
        var webSocketOptions = new WebSocketOptions
        {
            KeepAliveInterval = TimeSpan.FromMinutes(2)
        };

        app.UseWebSockets(webSocketOptions);
        // </snippet_UseWebSockets>

        app.UseDefaultFiles();
        app.UseStaticFiles();

        app.MapControllers();

        app.Run();
        }
    }

```

## Step 6 test locally

To test your .NET app locally, you can run it in Visual Studio or by using the following .NET CLI command: 

```bash
dotnet run --urls=https://localhost:5001/
```

## Step 7 deploy to app service

After you're satisfied with you websockets app, you can deploy to app service using the Azure CLI.

### Windows App Service Plan

To deploy your app, run the following Azure CLI commands: 

```azurecli-interactive
az webapp up --sku B1 --name <app-name> --resource-group <resource-group-name> --subscription <subscription-name>
az webapp config set --name <app-name> --resource-group <resource-group-name> --web-sockets-enabled true
```

The first command will create a Basic pricing tier webapp with your specified name in the resource group and subscription of your choice. The second command enables websockets for the same app created by the previous command. Without the second command, your webapp will not allow websocket connections, even if you're attempting to initialized a websocket server in your application.

### Linux App Service Plan

To deploy your app, run the following Azure CLI command: 

```azurecli-interactive
az webapp up --sku B1 --name <app-name> --resource-group <resource-group-name> --subscription <subscription-name> --os-type Linux
```

This command creates a Basic tier webapp with your specified name in the resource group and subscription of your choice. Note that to run a .NET app on Linux, you'll need to explicitly specify your OS type, otherwise the Azure CLI will default to Windows. Also note, enabling WebSockets is not required on Linux App Service Plans. 



## Clean up resources

When no longer needed, you can use the [az group delete](https://docs.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest#az-group-delete) command to remove the resource group, and all related resources:

```azurecli-interactive
az group delete --resource-group <resource-group-name>
```
