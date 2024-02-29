# gRPC Python App on App Service

### Steps to run the application
#### 1. Clone this repo

#### 2. Install dependencies
Run the following commands to set up your virtual environment and install all the necessary dependencies for the app.

The virtual environment is already created, activate our virtual environment with the following command:

> NOTE: If using the Visual Studio terminal, the virtual environment will be activated by default.  Skip this step.

```bash
source venv/bin/activate
```

Now with our virtual environment active, we can install our dependencies with:

```bash
pip3 install -r requirements.txt
```

#### 3. Run the app locally
To run this app locally, run `python app.py`. The gRPC service will start listening on port `8282`.The server app is now ready to receive requests from the client.

##### Start the client application
Once the application is running, you can start the client application. Run the client application with `python greeter_client.py` using another terminal. 

The client app will prompt you with a question for input to the gRPC server.

##### Deploying to App Service
After testing locally, you can deploy the application to App Service.  Create a linux web app and follow the **Deployment Steps** below to enable gRPC calls on your application.

### Deployment Steps

#### 1. Enable HTTP version
The first setting you'll need to configure is the HTTP version
1. Navigate to **Configuration** under **Settings** in the left pane of your web app
2. Click on the **General Settings** tab and scroll down to **Platform settings**
3. Go to the **HTTP version** drop-down and select **2.0**
4. Click **save**

This will restart your application and configure the front end to allow clients to make HTTP/2 calls.

#### 2. Enable HTTP 2.0 Proxy
Next, you'll need to configure the HTTP 2.0 Proxy:
1. Under the same **Platform settings** section, find the **HTTP 2.0 Proxy** setting and switch it to **On**.
2. Click **save**

Once turned on, this setting will configure your site to be forwarded HTTP/2 requests.

#### 3. Add HTTP20_ONLY_PORT application setting
Earlier, we configured the application to listen to a specific HTTP/2 only port.  Here we'll add an app setting HTTP20_ONLY_PORT and put the value as the port number we used earlier.
1. Navigate to the **Configuration** under **Settings** on the left pane of your web app.  
2. Under **Application Settings**, click on **New application setting**
3. Add the following app setting to your application
	1. **Name =** HTTP20_ONLY_PORT 
	2. **Value =** 8282

This setting will communicate to your web app which port is specified to listen over HTTP/2 only.

#### 4. Add SCM_DO_BUILD_DURING_DEPLOYMENT application setting
To ensure our application runs a `pip install` to resolve all our dependencies named in `requirements.txt`, we'll need to set the following application setting.
1. Navigate to the **Configuration** under **Settings** on the left pane of your web app.  
2. Under **Application Settings**, click on **New application setting**
3. Add the following app setting to your application
	1. **Name =** SCM_DO_BUILD_DURING_DEPLOYMENT 
	2. **Value =** true

#### 5. Add a custom startup command
To ensure your application starts up properly, we'll need to set a custom startup command to kick off our grpc and flask server.
1. Navigate to the **Configuration** under **Settings** on the left pane of your web app.
2. Under **General Settings**, add the following **Startup Command** `python app.py`

#### 6. Save your app configuration
Click the `Save` button at the top of the Configuration page. This will restart your application and apply all updated application settings.

#### 7. Deploy the application 
Run the following command to deploy your grpc app to App Service.
`az webapp up --name <app-name>`

#### 8. Test the application
Once deployed, replace the listening port in the local client application with the azurewebsites.net url of your app to test the deployed grpc server. This is found on line 34 of `greeter_client.py`.

To test the deployed version of the application, update your `insecure channel` to a `secure channel` on line 34 of `greeter_client.py`. Replace the current line with: 

```Python
with grpc.secure_channel('[APP_NAME].azurewebsites.net', creds) as channel:
```

Once deployed, you can make a call from a local client that will prompt you with a question.  The answer provided will be coming from the deployed server that uses your OpenAI API key and the LangChain predict method.

### Common Issues/Bugs
1. Forgetting to set or incorrectly setting any of the above application settings will result in a malfunctioning app
2. Remember to always start your grpc server before your flask server. In `app.py` running `app.run()` before `grpc_server = serve()` will prevent the grpc server from ever starting.
3. Forgetting to change the channel type of your grpc channel to a `secure channel` and updating the URL to your App Service URL
4. Including your grpc port number with your App Service URL in your channel connection.  It's not needed.
