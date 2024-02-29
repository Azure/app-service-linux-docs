# How to use the gRPC client 
As is, the client is setup for local development.  These are the steps to run the application locally:

1. Clone the repository
2. Run the `npm install` command to install the npm packages
3. Run the `node app.js` command to run the application

To use this client to make a unary call to a Node gRPC server hosted on App Service follow these directions:

1. Clone the repository
2. Run the `npm install` command to install the npm packages
3. Update the target in the `app.js` file to point to your hosted application

```
target = '<your-app-name>.azurewebsites.net';
```

4. Update the client variable in the `app.js` file to use the `grpc.credentials.createFromSecureContext();` credentials

```
   var client = new hello_proto.Greeter(target,
        grpc.credentials.createFromSecureContext());
```

5. Run the `node app.js` command to run the application


