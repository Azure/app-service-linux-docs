# How to deploy a .NET 8 application using gRPC on Windows App Service (preview)

> [!NOTE]
> gRPC on Windows App Service is a **Preview** feature for .NET workloads only.

> [!NOTE]
> gRPC on Windows App Service is currently compatible with in-process hosting only.

> [!NOTE]
> gRPC on Windows App Service currently does not work with Windows containers

The following is a tutorial on how to deploy a .NET 8 gRPC application on Windows App Service.

### Prerequisite

In this tutorial, we'll be deploying a gRPC server to App Service and making a gRPC request to the deployed server from a local gRPC client. If you have not created a gRPC client and server yet, please follow this [ASP.NET Core tutorial](https://docs.microsoft.com/aspnet/core/tutorials/grpc/grpc-start?view=aspnetcore-6.0&tabs=visual-studio#create-a-grpc-service) to do so.

The following tutorial builds from the created gRPC client and server in that documentation. If you already have a gRPC client and server, you may use these steps to add to existing .NET apps as well.

**Setup the gRPC Server app**

If you haven't already done so when testing your gRPC server application locally in the previous tutorial, set the `launchBrowser` property to `true` in your `launchSettings.json` file. This will launch the browser in local development and show the expected web page we will see when deployed to App Service

### Deploy to App Service

Create your web app as you normally would. Choose **Code** as your Publish option. Choose **.NET 8 (LTS)** as your Runtime stack and **Windows** as your Operating System.

Now that your web app is created, you'll need to do the following before deploying your application:

1. **Configure the HTTP version**

The first setting that you need to configure is the HTTP version:

1. On the left pane of your web app, under **Settings**, go to **Configuration**.
2. On the **General Settings** tab, scroll down to **Platform settings**.
3. In the **HTTP version** dropdown list, select **2.0**.
4. Select **Save**.

This setting restarts your application and configures the front end to allow clients to make HTTP/2 calls.

1. **Configure the HTTP 2.0 proxy**

Next, you need to configure the HTTP 2.0 proxy:

1. Navigate to the [resource explorer](https://resources.azure.com/) and find your application
    1. Find your application through the following path (click on the **+** signs):
        1. **+ subscriptions > + your-subscription-name > + resourceGroups > + your-resource-group-name > + Providers > + Microsoft.Web > + sites > your-site-name > + config > web**
2. Click on **Edit**
3. Find the **“http20ProxyFlag”** property and updated the value to **1**
4. Click the **PUT** button to save the new value

This setting will configure your site to receive HTTP/2 requests.

1. **Enable End to End Encryption**

Lastly, App Service requires End to End encryption to be enabled.  

1. Navigate to the [resource explorer](https://resources.azure.com/) and find your application
    1. Find your application through the following path (click on the **+** signs):
        1. **+ subscriptions > + your-subscription-name > + resourceGroups > + your-resource-group-name > + Providers > + Microsoft.Web > + sites > your-site-name**
2. Click on **Edit**
3. Find the **“endToEndEncryptionEnabled”** property and updated the value to **true**
4. Click the **PUT** button to save the new value

Now that the app is created and configurations are set, we can publish from Visual Studio. 

1. Right click on the project and select **Publish** 
2. Choose **Azure App Service (Windows)** as the target
3. Navigate to your application, click **Finish** and **Close**

Then, click the **Publish** button to publish to your Web App.  Once published your app is now ready to accept gRPC requests at the provided URL endpoint.

**Confirm a gRPC request call from your local client**

Now that the gRPC service is deployed and we have a URL from our deployed Web App, we can make a call from our local client to test that our channel connects to the server and that our client can receive a response.

Navigate back to the **Program.cs** file and swap out the localhost address for the App Service URL.

> Note: gRPC calls must be over https. Insecure calls are not possible.
> 

```csharp
// replace the localhost address with your App Service URL
using var channel = GrpcChannel.ForAddress("https://you-app-name.azurewebsites.net/");
```

Now save your application and run the local client (Ctrl+F5). Your console application should receive and display the message from your gRPC service. If you used the server from the ASP.NET tutorial, it will read the same message:

```bash
Greeting: Hello GreeterClient
Press any key to exit...
```

The response from your deployed server will be shown using the updated channel. If this is shown you have successfully deployed your gRPC server application to App Service.