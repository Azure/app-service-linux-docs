#### 1. Open the `GrpcGreeterServer` app in Visual Studio or VS Code
#### 2. Run the app locally
To run this app locally, use Ctrl+F5 to start the app.  The gRPC service will start listening on `http://localhost:8585` and will be ready to accept a request from the `GrpcGreeterClient` app.


#### 3. Deploy to App Service
Before deploying this sample to App Service you'll need to add a few configuration steps. Follow the directions in this [How-To](https://review.learn.microsoft.com/azure/app-service/configure-grpc?branch=main) to setup your Web App to run a gRPC service.  