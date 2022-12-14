# How-to deploy a .NET 7 gRPC app on App Service

> [!WARNING]
> gRPC is currently available to try as a Public Preview feature.

gRPC is a Remote Procedure Call framework that is used to streamline messages between your client and server over HTTP/2.  Using gRPC protocol over HTTP/2 enables the use of features like multiplexing to send multiple parallel requests over the same connection and bi-directional streaming for sending requests and responses simultaneously.  

The following is a tutorial on how to deploy a .NET 6 gRPC application on App Service. 

#### Prerequisite
In this tutorial, we'll be deploying a gRPC server to App Service and making a gRPC request to the deployed server from a local gRPC client.  If you have not created a gRPC client and server yet, please follow this [ASP.NET Core tutorial](https://docs.microsoft.com/aspnet/core/tutorials/grpc/grpc-start?view=aspnetcore-6.0&tabs=visual-studio#create-a-grpc-service) to do so.  

The following tutorial builds from the created gRPC client and server in that documentation.  If you already have a gRPC client and server, you may use these steps to add to existing .NET apps as well.  If you would like to view .NET 6 and .NET Core 3.1 samples, please visit [here](https://github.com/Azure/app-service-linux-docs/tree/master/HowTo/gRPC).


### Deploy to App Service
Before deploying to App Service, note that gRPC is currently only supported on Linux so be sure to choose this option when creating your web app.

Create your web app as you normally would.  Choose **Code** as your Publish option.  Choose **.NET 7 (STS)** as your Runtime stack and **Linux** as your Operating System.  

Now that your web app is created, you'll need to do the following before deploying your application:

#### Add HTTP20_ONLY_PORT application setting
App Service requires an application setting that specifically listens for HTTP/2 traffic.  Here we'll add an app setting HTTP20_ONLY_PORT and put the value from the launchSettings.json file as the port number.
1. Navigate to the **Configuration** under **Settings** on the left pane of your web app.  
2. Under **Application Settings**, click on **New application setting**
3. Add the following app setting to your application.  The value for the port used here is found in the `launchSettings.json` file as the `"applicationUrl"` value.
	1. **Name =** HTTP20_ONLY_PORT 
	2. **Value =** 5243 
4

This setting will communicate to your web app which port is specified to listen over HTTP/2 only.

### Configuration
When deploying to App Service using .NET 7 the following configuration settings are set for you:

1. **HTTP version** is set to **2.0**.  This setting configures the front end to allow clients to make HTTP/2 calls.
2. **HTTP 2.0 Proxy** is set to **On**.  This setting enables the front end to forward HTTP/2 traffic to the worker.

These settings are required to enable gRPC.



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

