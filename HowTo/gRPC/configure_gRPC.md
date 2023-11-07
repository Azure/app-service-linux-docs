# Configure gRPC on App Service

This article explains how to configure your Web App for gRPC.  

gRPC is a Remote Procedure Call framework that is used to streamline messages between your client and server over HTTP/2.  Using gRPC protocol over HTTP/2 enables the use of features like multiplexing to send multiple parallel requests over the same connection and bi-directional streaming for sending requests and responses simultaneously.  Support for gRPC on App Service (Linux) is currently available.  

The following is the configuration steps needed to deploy a gRPC application on App Service. 

> For gRPC client and server samples for each supported language, please visit the [documentation on GitHub](https://github.com/Azure/app-service-linux-docs/tree/master/HowTo/gRPC). 

### Create your Web App
Create your [Web App](https://learn.microsoft.com/azure/app-service/getting-started?pivots=stack-net) as you normally would.  Choose your preferred Runtime stack and **Linux** as your Operating System.

Now that your web app is created, you'll need to do the following before deploying your application:

>NOTE: If you are deploying a .NET gRPC app to App Service with Visual Studio, skip to step 3.  Visual Studio will set the HTTP version and HTTP 2.0 Proxy configuration for you. 

#### 1. Enable HTTP version
The first setting you'll need to configure is the HTTP version
1. Navigate to **Configuration** under **Settings** in the left pane of your web app
2. Click on the **General Settings** tab and scroll down to **Platform settings**
3. Go to the **HTTP version** drop-down and select **2.0**
4. Click **save**

This will restart your application and configure the front end to allow clients to make HTTP/2 calls.

#### 2. Enable HTTP 2.0 Proxy
Next, you'll need to configure the HTTP 2.0 Proxy:
1. Under the same **Platform settings** section, find the **HTTP 2.0 Proxy** setting and select **gRPC Only**.
2. Click **save**

Once turned on, this setting will configure your site to be forwarded HTTP/2 requests.

#### 3. Add HTTP20_ONLY_PORT application setting
App Service requires an application setting that specifically listens for HTTP/2 traffic.
1. Navigate to the **Environment variables** under **Settings** on the left pane of your web app.  
2. Under the **App settings** tab, add the following app setting to your application.
	1. **Name =** HTTP20_ONLY_PORT 
	2. **Value =** 8585

This setting will configure the port on your application that is specified to listen for HTTP/2 request.

Once these three steps are configured, you can successfully make HTTP/2 calls to your Web App with gRPC.  

## FAQ

> gRPC is not a supported feature on ASEv2 SKUs.  Please use an ASEv3 SKU.

### OS support
Currently gRPC is a Linux only feature.  Support for Windows is coming in 2024 for .NET workloads.

### Language support
gRPC is supported for each language that supports gRPC.  

### Client Certificates
HTTP/2 enabled on App Service does not currently support client certificates.  Client certificates will need to be ignored when using gRPC.

### Secure calls
gRPC must make secure HTTP calls to App Service.  You cannot make insecure calls.

### Activity Timeout
gRPC requests on App Service have a timeout request limit.  gRPC requests will timeout after 20 minutes of inactivity.  
