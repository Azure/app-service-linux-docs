#### 1. Open the `grpcgreeterserver31` app in Visual Studio or VS Code
#### 2. Deploy to App Service
Before deploying this sample to App Service make sure the following line in *Program.cs* file is uncommented.  This line will cause an error when deployed if left commented out.

```c#
options.ListenAnyIp(8080);
```
Next, follow the directions in this [How-To](https://github.com/Azure/app-service-linux-docs/blob/master/HowTo/gRPC/use_gRPC_with_dotnet.md) to setup your web app to run a gRPC service.  