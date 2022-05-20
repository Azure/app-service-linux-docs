
#### Steps to run:
#### 1. Open the `GrpcGreeterClient` app in Visual Studio or VS Code
#### 2. Run the app locally
To run this app locally, first start the gRPC server app `GrpcGreeterServer` first.

`GrpcGreeterServer` is listening on `http://localhost:8181`.  The gRPC channel in this client is already pointing to this address.  

Use Ctrl+F5 to start the app and make a call to your local `GrpcGreeterServer`.

#### 3. Point to deployed gRPC service
If your `GrpcGreeterServer` is deployed on App Service, you can use this same client to make calls to it.  Simply replace `http://localhost:8181` with your deployed URL. 

```
using var channel = GrpcChannel.ForAddress("https://my-grpc-app-name.azurewebsites.net/");
```




