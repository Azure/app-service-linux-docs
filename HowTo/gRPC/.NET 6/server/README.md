#### 1. Open the `GrpcGreeterServer` app in Visual Studio or VS Code
#### 2. Run the app locally
To run this app locally, use Ctrl+F5 to start the app.  The gRPC service will start listening on `http://localhost:8181` and will be ready to accept a request from the `GrpcGreeterClient` app.


#### 3. Deploy to App Service
Before deploying this sample to App Service you'll need to uncomment the following line in the *Program.cs* file.  This line will cause an error when deployed if left commented out.

```c#
options.ListenAnyIp(8080);
```
Next, follow the directions in this [How-To]() to setup your web app to run a gRPC service.  