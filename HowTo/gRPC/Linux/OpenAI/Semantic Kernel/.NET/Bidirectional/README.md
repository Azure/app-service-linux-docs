# gRPC + Express on App Service

##### Deploying to App Service

1. Clone the repo
2. Create a linux web app on App Service and use the configuration steps below to enable gRPC calls on your application.
3. Deploy the server application to your web app

### Web App Configuration

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
Configure the application to listen to a specific HTTP/2 only port.
1. Navigate to the **Configuration** under **Settings** on the left pane of your web app.  
2. Under **Application Settings**, click on **New application setting**
3. Add the following app setting to your application
	1. **Name =** HTTP20_ONLY_PORT 
	2. **Value =** 8282