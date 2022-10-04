# How to use websockets with Django in App Service

> **NOTE**:
>
> - These instructions only apply to Linux app service plans
> - These instructions are for Django and Python 3.X only

Websockets are a great tool for bi-directional messaging and can be used with App Service. In this tutorial, we will create a simple chat client/server using websockets and Node.js. The chat app is based off of the following tutorial from [Channels](https://channels.readthedocs.io/en/stable/tutorial/part_1.html), the library we'll use to make a simple realtime chat application using websockets.

## Prerequisites

This guide uses the [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest) to configure your resources. If you don't want to install the Azure CLI locally, you can always use [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/quickstart).

This guide also assumes that you have [Python 3](https://www.python.org/downloads/) installed locally. 

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

## Step 0.2 install Django in our virtual environment

Before we can create a Django app, we'll need to have Django installed. Assuming your virtual environment is still active from the last step, run the following command to install Django.

```bash
pip3 install Django
```

## Step 1 create a Django app

With Django installed we can now create our Django app. Run the following command to create the directory structure for your new application.

```bash
django-admin startproject <app-name>
```

After this command executes, open the newly created `<app-name>` directory in VSCode or another text editor to view the contents. We'll be modifying these to create our websockets application. Also, be sure to change directory in your terminal to your `<app-name>` directory. We'll need to manage our app from there. An example of the Django app directory structure is shown below.

```
<app-name>/
    manage.py
    <app-name>/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
```

## Step 2 create a requirements.txt and install all remaining dependencies

Now that we have a Django app directory structure, we can create a requirements.txt to keep track of all our dependencies. This requirements.txt file should be created at the root of our Django app, within the outer `<app-name>` directory that contains our manage.py file and an inner `<app-name>` directory. 

The requirements.txt file should contain the following dependencies:

```
Django
channels
gunicorn
uvicorn
uvicorn[standard]
websockets
```

Our application structure should now look like this: 

```
<app-name>/
    manage.py
    requirements.txt
    <app-name>/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
```

Now we just need to install these dependencies by running the following command from our application root directory.

```bash
pip3 install -r requirements.txt
```

## Step 3 create a chat app to hold our chat server application

With our dependencies sorted, we can now start building our application by creating an additional app inside our Django project called `chat` using the following command:


```bash
python3 manage.py startapp chat
```

Our new directory structure after this command looks like this: 

```
<app-name>/
    manage.py
    requirements.txt
    <app-name>/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    chat/
        __init__.py
        admin.py
        apps.py
        migrations/
            __init__.py
        models.py
        tests.py
        views.py
```

## Step 4 add the new chat app to `<app-name>/<app-name>/settings.py`

After creating our chat app, we now need to add it to our INSTALLED_APPS in `<app-name>/<app-name>/settings.py`. We'll also add the `channels` app for later. After adding `chat` and `channels` to our INSTALLED_APPS, it should look something like this:

```python
INSTALLED_APPS = [
    'chat',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

## Step 5 add index and room views to our chat app

Now we need to create our views for the app, which will live in `<app-name>/chat/templates/chat/`. 

Our first view will be index.html and should be created with the following path: `<app-name>/chat/templates/chat/index.html`. The contents of our index are included below: 

```html
<!-- chat/templates/chat/index.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Chat Rooms</title>
</head>
<body>
    What chat room would you like to enter?<br>
    <input id="room-name-input" type="text" size="100"><br>
    <input id="room-name-submit" type="button" value="Enter">

    <script>
        document.querySelector('#room-name-input').focus();
        document.querySelector('#room-name-input').onkeyup = function(e) {
            if (e.keyCode === 13) {  // enter, return
                document.querySelector('#room-name-submit').click();
            }
        };

        document.querySelector('#room-name-submit').onclick = function(e) {
            var roomName = document.querySelector('#room-name-input').value;
            window.location.pathname = '/chat/' + roomName + '/';
        };
    </script>
</body>
</html>
```

In the same directory as our index, we'll need to create a room.html to act as the default UI for our chat rooms. This is effectively our websocket client that will allow us to both send and receive messages. The path for this file is `<app-name>/chat/templates/chat/room.html` and the contents are shown below: 

```html
<!-- chat/templates/chat/room.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Chat Room</title>
</head>
<body>
    <textarea id="chat-log" cols="100" rows="20"></textarea><br>
    <input id="chat-message-input" type="text" size="100"><br>
    <input id="chat-message-submit" type="button" value="Send">
    {{ room_name|json_script:"room-name" }}
    <script>
        const roomName = JSON.parse(document.getElementById('room-name').textContent);

        // 'wss://' is required for app service, must be switched to 'ws://' for local testing
        const chatSocket = new WebSocket(
            'wss://'
            + window.location.host
            + '/ws/chat/'
            + roomName
            + '/'
        );

        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            document.querySelector('#chat-log').value += (data.message + '\n');
        };

        chatSocket.onclose = function(e) {
            console.log(e);
            console.error('Chat socket closed unexpectedly');
        };

        document.querySelector('#chat-message-input').focus();
        document.querySelector('#chat-message-input').onkeyup = function(e) {
            if (e.keyCode === 13) {  // enter, return
                document.querySelector('#chat-message-submit').click();
            }
        };

        document.querySelector('#chat-message-submit').onclick = function(e) {
            const messageInputDom = document.querySelector('#chat-message-input');
            const message = messageInputDom.value;
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInputDom.value = '';
        };
    </script>
</body>
```

With our html files created, we'll now need to edit our `<app-name>/chat/views.py` file to contain the following references to our html templates: 

```python
# chat/views.py
from django.shortcuts import render

def index(request):
    return render(request, 'chat/index.html', {})

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })
```

After editing our views.py file, we need to create two urls.py files to map our views to the correct URLs. The first one to create is `<app-name>/chat/urls.py` with the following contents: 

```python
# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
]
```

We'll also need `<app-name>/<app-name>/urls.py` to contain: 

```python
# mysite/urls.py
from django.conf.urls import include
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('', include('chat.urls')),
    path('chat/', include('chat.urls')),
    path('admin/', admin.site.urls),
]
```

Our directory structure should now look like this: 

```
<app-name>/
    manage.py
    requirements.txt
    <app-name>/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    chat/
        __init__.py
        admin.py
        apps.py
        migrations/
            __init__.py
        models.py
        templates/chat/
            index.html
            room.html
        tests.py
        urls.py
        views.py
```

## Step 6 create a chat consumer

Our consumer needs to be able to handle events from a websocket connection after the connection itself has been established using the channels library. Our `<app-name>/chat/consumers.py` file needs to contain the following contents: 

```python
# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
```

Our directory structure should no look like this: 

```
<app-name>/
    manage.py
    requirements.txt
    <app-name>/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    chat/
        __init__.py
        admin.py
        apps.py
        consumers.py
        migrations/
            __init__.py
        models.py
        templates/chat/
            index.html
            room.html
        tests.py
        urls.py
        views.py
```

## Step 7 add routing configuration for consumer

Now we'll need to be able to route to the consumer we just created. We can accomplish this by making a new `<app-name>/chat/routing.py` file with the following contents: 

```python
# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
```

Our directory structure should now look like this: 

```
<app-name>/
    manage.py
    requirements.txt
    <app-name>/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    chat/
        __init__.py
        admin.py
        apps.py
        consumers.py
        migrations/
            __init__.py
        models.py
        routing.py
        templates/chat/
            index.html
            room.html
        tests.py
        urls.py
        views.py
```

## Step 8 integrate the channels library for websocket usage

To integrate the channels library we first need to create an asgi app in `<app-name>/<app-name>/asgi.py` with the following contents: 

```python
# mysite/asgi.py
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chat_sample.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
```

We also need to tell Django about our newly created asgi app by appending the following line to the bottom of our `<app-name>/<app-name>/settings.py` file: 

```python
ASGI_APPLICATION = '<app-name>.asgi.application'
```

## Step 9 add an in-memory channel layer to handle our websocket messages

A channel layer allows multiple consumers to communicate with each other. We've already created our consumer in a previous step, and now we just need to append the following lines to the bottom of our `<app-name>/<app-name>/settings.py` file to enable an in-memory channel layer: 

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

## Step 10 test locally

To test locally, be sure to first temporarily switch the `wss://` to `ws://` in `<app-name>/chat/templates/chat/room.html`. 

Now run the following uvicorn command from your `<app-name>/` directory to test the application and enure our websockets are working properly. The app should allow you to enter a chat room and send messages to any other client with the same chat room open.

```
uvicorn --host 0.0.0.0 <app-name>.asgi:application
```

## Step 11 deploy to app service

After you're satisfied with you websockets app, you can deploy to app service using the Azure CLI. 

**IMPORTANT** ensure your websocket URL is using `wss://` and **NOT** `ws://` in `<app-name>/chat/templates/chat/room.html`. 

To deploy your app, run the following Azure CLI commands: 

```bash
az webapp up --sku B1 --name <app-name> --resource-group <resource-group-name> --subscription <subscription-name>
az webapp config set --name <app-name> --resource-group  <resource-group-name> --startup-file "uvicorn --host 0.0.0.0 <app-name>.asgi:application"
```

The first command will create a Basic pricing tier webapp with your specified name in the resource group and subscription of your choice. The second command sets a custom startup script to use uvicorn to kick off our Django app. 

The custom startup script is required since App Service assumes you'll be using a wsgi app and will automatically use gunicorn to start the application. This won't work for asgi apps, which means we'll need to use a custom script to start our app properly.

## Troubleshooting

If your application refuses to properly start or your websockets refuse to connect, first make sure your `<app-name>/chat/templates/chat/room.html` is using `wss://` for websocket connections. 

For any additional problems, like dependencies not being installed at runtime or the application failing to start, try performing a .zip deployment. To .zip deploy, compress all Django related files into a .zip archive and deploy it App Service with the following command: 

```bash
az webapp deploy --src-path <application-zip-name>.zip
```

## Clean up resources

When no longer needed, you can use the [az group delete](https://docs.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest#az-group-delete) command to remove the resource group, and all related resources:

```azurecli-interactive
az group delete --resource-group <resource-group-name>
```
