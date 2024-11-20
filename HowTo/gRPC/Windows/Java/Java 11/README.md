
> ## Support Status
> gRPC on Windows App Service is currently a **preview** feature that is enabled using in-process hosting only with ASP.NET.  Additional support for out-of-proc scenarios, Windows container, and Java support is being worked on and planned for 2025.  Site activation through gRPC is also not yet supported and must have Always On turned on in the configuration settings.  


## Run the app locally

Before deploying your application, test the application locally to ensure it works as expected. Clone the repository and follow the steps below.

#### Start the server
1. Open the `spring-boot-server` project in Visual Studio Code or Visual Studio.
1. Run the command `mvn clean install` to build the project.
1. Run the command `mvn spring-boot:run` to start the server.

Once started, you will see `gRPC server started` in the terminal. Your server is now running and listening for requests.

#### Start the client
1. Open the `Client` project in Visual Studio Code or Visual Studio.
1. Run the command `mvn clean install` to build the project.
1. Run the command `mvn exec:java` or `ctrl + F5` to start the client.

Once started, you will see `gRPC client started` in the terminal. Your client is now running and ready to make requests to the server. Press `Enter` to make a request to the server and follow the instructions in the terminal.


### Deploy the app to Windows App Service
TBD!!
