#### Steps to run:
#### 1. Open the `grpcgreeterclient31` app in Visual Studio or VS Code
#### 2. Point to deployed gRPC service
If your `grpcgreeterserver31` app is deployed on App Service, you can use this client to make calls to it.  Simply replace `http://localhost:8282` with your deployed URL and run it locally.  

```c#
using var channel = GrpcChannel.ForAddress("https://my-grpc-app-name.azurewebsites.net/");
```