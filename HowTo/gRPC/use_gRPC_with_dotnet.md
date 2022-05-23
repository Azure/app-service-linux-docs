# How-to deploy a .NET 6 gRPC app on App Service

> [!WARNING]
> The following documentation is dependent on a future release of App Service that is not currently available to the public.  gRPC is currently available to try in EUAP with Private Preview.

gRPC is a Remote Procedure Call framework that is used to streamline messages between your client and server over HTTP/2.  Using gRPC protocol over HTTP/2 enables the use of features like multiplexing to send multiple parallel requests over the same connection and bi-directional streaming for sending requests and responses simultaneously.  

The following is a tutorial on how to deploy a .NET 6 gRPC application on App Service. 

#### Prerequisite
In this tutorial, we'll be deploying a gRPC server to App Service and making a gRPC request to the deployed server from a local gRPC client.  If you have not created a gRPC client and server yet, please follow this [ASP.NET Core tutorial](https://docs.microsoft.com/aspnet/core/tutorials/grpc/grpc-start?view=aspnetcore-6.0&tabs=visual-studio#create-a-grpc-service) to do so.  

The following tutorial builds from the created gRPC client and server in that documentation.  If you already have a gRPC client and server, you may use these steps to add to existing .NET apps as well.  If you would like to view .NET 6 and .NET Core 3.1 samples, please visit [here](https://github.com/Azure/app-service-linux-docs/tree/master/HowTo/gRPC).

### Setup the gRPC Server app
In order to prepare our gRPC server application to deploy to App Service, we will need to configure Kestrel to listen to an additional port that only listens for plain-text HTTP/2.

In your **Program.cs** add the following code to configure Kestrel.  In this example we're listening to port 8585, but you can use another number.

```C#
// Configure Kestrel to listen on a specific HTTP port 
builder.WebHost.ConfigureKestrel(options => 
{ 
    options.ListenAnyIP(8080); 
    options.ListenAnyIP(8585, listenOptions => 
    { 
        listenOptions.Protocols = Microsoft.AspNetCore.Server.Kestrel.Core.HttpProtocols.Http2; 
    }); 
});

```

Once configured this will ensure that your application is listening to a specific HTTP/2 only port, which will be needed when we deploy to App Service. 

If you are using the templated code from the ASP.NET tutorial we will need to remove the EndpointDefaults configuration in the appsettings.json file.  In the **appsettings.json** file, remove the commented code below.

```jsonc
{ 
  "Logging": { 
    "LogLevel": { 
      "Default": "Information", 
      "Microsoft.AspNetCore": "Warning" 
    } 
  }, 
  "AllowedHosts": "*", 
  //  "EndpointDefaults": { 
  //    "Protocols": "Http2" 
  //  } 
  //} 
}

```
We no longer need this code since we have configured the protocol options in our Program.cs file and it will cause an error if deployed.  Once this is done your application is now ready to deploy to App Service.

### Deploy to App Service
Now that you have your server application setup and running locally, you can go to the portal and create your web app.  One thing to note is that gRPC is currently only supported on Linux so be sure to choose this option when creating your web app.

Create your web app as you normally would.  Choose **Code** as your Publish option.  Choose **.NET 6 (LTS)** as your Runtime stack and **Linux** as your Operating System.  

Now that your web app is created, you'll need to do the following before deploying your application:

#### 1. Enable HTTP version
The first setting you'll need to configure is the HTTP version
1. Navigate to **Configuration** under **Settings** in the left pane of your web app
2. Click on the **General Settings** tab and scroll down to **Platform settings**
3. Go to the **HTTP version** drop-down and select **2.0**
4. Click **save**

This will restart your application and configure the front end to allow clients to make HTTP/2 calls.

#### 2. Enable HTTP20ProxyFlag
Next, you'll need to configure the HTTP20ProxyFlag:
1. Type in [resources.azure.com](https://resources.azure.com) to navigate to the Azure Resource Explorer
2. go to the left pane and click on + subscriptions
3. find and click on your subscription from the list
4. click on + resourceGroups under your subscription name
5. find your resource group and click on your resource group name
6. click on + providers under your resource group
7. click on + Microsoft.web
8. click on + sites
9. click on the name of your site + mygrpcgreeterapp
10. go to the open pane to the right and click on edit
11. scroll down and find the siteConfig property 
12. under siteConfig, find http20ProxyFlag
13. update the value from null to 1
14. navigate to the top of the pane and click PUT

Once clicked, a green checkmark will flash on the screen.  This setting will configure your site to be forwarded HTTP/2 requests.

#### 3. Add HTTP20_ONLY_PORT application setting
Earlier, we configured the application to listen to a specific HTTP/2 only port.  Here we'll add an app setting HTTP20_ONLY_PORT and put the value as the port number we used earlier.
1. Navigate to the **Configuration** under **Settings** on the left pane of your web app.  
2. Under **Application Settings**, click on **New application setting**
3. Add the following app setting to your application
	1. **Name =** HTTP20_ONLY_PORT 
	2. **Value =** 8585

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
