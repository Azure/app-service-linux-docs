# How-to deploy a .NET 6 gRPC app on App Service

> [!WARNING]
> gRPC is currently available to try as a Public Preview feature.

> gRPC is not a supported feature on ASEv2 SKUs.  If you would like to use this feature with an Isolated SKU, you must use ASEv3.

gRPC is a Remote Procedure Call framework that is used to streamline messages between your client and server over HTTP/2.  Using gRPC protocol over HTTP/2 enables the use of features like multiplexing to send multiple parallel requests over the same connection and bi-directional streaming for sending requests and responses simultaneously.  

The following is a tutorial on how to deploy a .NET 6 gRPC application on App Service. 

#### Prerequisite
In this tutorial, we'll be deploying a gRPC server to App Service and making a gRPC request to the deployed server from a local gRPC client.  If you have not created a gRPC client and server yet, please follow this [ASP.NET Core tutorial](https://docs.microsoft.com/aspnet/core/tutorials/grpc/grpc-start?view=aspnetcore-6.0&tabs=visual-studio#create-a-grpc-service) to do so.  

The following tutorial builds from the created gRPC client and server in that documentation.  If you already have a gRPC client and server, you may use these steps to add to existing .NET apps as well.  If you would like to view .NET 6 and .NET Core 3.1 samples, please visit [here](https://github.com/Azure/app-service-linux-docs/tree/master/HowTo/gRPC).

### Setup the gRPC Server app
If you haven't already done so when testing your gRPC server application locally, set the `launchBrowser` property to `true` in your `launchSettings.json` file.  This will ensure your browser doesn't show an error when visiting the URL.

### Deploy to App Service
Before deploying to App Service, note that gRPC is currently only supported on Linux so be sure to choose this option when creating your web app.

Create your web app as you normally would.  Choose **Code** as your Publish option.  Choose **.NET 6 (LTS)** as your Runtime stack and **Linux** as your Operating System.  

Now that your web app is created, you'll need to do the following before deploying your application:

>NOTE: If you are deploying to App Service with Visual Studio, you can skip the first two steps.  Visual Studio will set those for you.

#### 1. Enable HTTP version - (skip this step if deploying from Visual Studio)
The first setting you'll need to configure is the HTTP version
1. Navigate to **Configuration** under **Settings** in the left pane of your web app
2. Click on the **General Settings** tab and scroll down to **Platform settings**
3. Go to the **HTTP version** drop-down and select **2.0**
4. Click **save**

This will restart your application and configure the front end to allow clients to make HTTP/2 calls.

#### 2. Enable HTTP 2.0 Proxy - (skip this step if deploying from Visual Studio)
Next, you'll need to configure the HTTP 2.0 Proxy:
1. Under the same **Platform settings** section, find the **HTTP 2.0 Proxy** setting and switch it to **On**.
2. Click **save**

Once turned on, this setting will configure your site to be forwarded HTTP/2 requests.

#### 3. Add HTTP20_ONLY_PORT application setting
App Service requires an application setting that specifically listens for HTTP/2 traffic.  Here we'll add an app setting HTTP20_ONLY_PORT and put the value from the launchSettings.json file as the port number.
1. Navigate to the **Configuration** under **Settings** on the left pane of your web app.  
2. Under **Application Settings**, click on **New application setting**
3. Add the following app setting to your application.  The value for the port used here is found in the `launchSettings.json` file as the `"applicationUrl"` value.
	1. **Name =** HTTP20_ONLY_PORT 
	2. **Value =** 5243

This setting will communicate to your web app which port is specified to listen over HTTP/2 only.

### Confirm a gRPC request call from your local client
Now that the gRPC service is deployed and we have a URL, we can make a call from our local client to test that our channel connects to the server and that our client can receive a response.

Navigate back to the **Program.cs** file and swap out the localhost address for the App Service URL.  

> Note: gRPC calls must be over https.  Insecure calls are not possible.

```C#
// replace the localhost address with your App Service URL
using var channel = GrpcChannel.ForAddress($"https://mygrpcapp.azurewebsites.net/");
```

Now save your application and run the local client (Ctrl+F5).  Your console application should receive and display the message from your gRPC service.  If you used the server from the ASP.NET tutorial, it will read the same message:

```Console
Greeting: Hello GreeterClient 
Press any key to exit...
```

The response from your deployed server will be shown using the updated channel.  If this is shown you have successfully deployed your gRPC server application to App Service.

#### Resources
1. [Create a .NET Core gRPC client and server in ASP.NET Core | Microsoft Docs](https://docs.microsoft.com/aspnet/core/tutorials/grpc/grpc-start?view=aspnetcore-6.0&tabs=visual-studio)
2. [Troubleshoot gRPC on .NET Core | Microsoft Docs](https://docs.microsoft.com/aspnet/core/grpc/troubleshoot?view=aspnetcore-6.0#call-a-grpc-service-with-an-untrustedinvalid-certificate)
