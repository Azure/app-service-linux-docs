# Configure gRPC on Windows App Service (preview)

> [!NOTE]
> gRPC on Windows App Service is a **Preview** feature for .NET workloads only.


> [!NOTE]
> gRPC on Windows App Service currently does not work with Windows containers


This article explains how to configure your web app for gRPC on Windows.

gRPC is a Remote Procedure Call framework that can streamline messages between your client and server over HTTP/2. Using the gRPC protocol over HTTP/2 enables the use of features like:

- Multiplexing to send multiple parallel requests over the same connection.
- Bidirectional streaming to send requests and responses simultaneously.

To use gRPC with your web app, you need to configure your app by selecting the HTTP version, proxy, and enabling end to end encryption.

For a gRPC client and server sample and walkthrough, please see the [documentation on GitHub](https://github.com/Azure/app-service-linux-docs/tree/master/HowTo/gRPC/Windows/.NET%208).

### Prerequisite

---

Create your [web app](https://learn.microsoft.com/en-us/azure/app-service/getting-started) as you normally would. Choose your preferred runtime stack, and choose Windows as your operating system.

After you create your web app, configure the following details to enable gRPC before you deploy your application.

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