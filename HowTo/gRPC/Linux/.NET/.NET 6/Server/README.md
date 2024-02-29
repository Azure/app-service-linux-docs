#### 1. Open the `GrpcGreeterServer` app in Visual Studio or VS Code
#### 2. Run the app locally
To run this app locally, use Ctrl+F5 to start the app.  The gRPC service will start listening on `http://localhost:8585` and will be ready to accept a request from the `GrpcGreeterClient` app.

1. If deploying locally, make sure that the Kestrel settings in the `appsettings.json` file are commented in.  This will ensure the server is sending HTTP/2 responses back to the client.

``` c#
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  // Comment Kestrel settings in for local development | Leave commented when deployed 
  "Kestrel": {
    "EndpointDefaults": {
      "Protocols": "Http2"
    }
  }
}

``` 


#### 3. Deploy to App Service

1. For this sample, you need to make sure the kestrel settings are commented out before deployment or it will give an error when deployed.  In the `appsettings.json` file, comment out the kestrel settings.

``` c#
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  // Comment Kestrel settings in for local development | Leave commented when deployed 
  //"Kestrel": {
  //  "EndpointDefaults": {
  //    "Protocols": "Http2"
  //  }
  //}
}

``` 


Before deploying this sample to App Service you'll need to add a few configuration steps. Follow the directions in this [How-To](https://review.learn.microsoft.com/azure/app-service/configure-grpc?branch=main) to setup your Web App to run a gRPC service.  