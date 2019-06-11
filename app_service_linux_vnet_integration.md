## Linux App Service VNet Integration

Azure Virtual Network (VNet) integration for Linux Web App is currently in Preview. Customers can use the VNet feature for development and integration testing with your web apps. Please do not use the feature for production purposes. Learn about how to [configure VNet with your web app](https://docs.microsoft.com/en-us/azure/app-service/web-sites-integrate-with-vnet#managing-the-vnet-integrations).  

During Preview you would need to modify your application in order to integrate with VNet. This is a temporary limitation during VNet Preview release, we will remove the limitation before GA.  In your application, please use the PORT environment variable as the main web server’s listening port, instead of using a hardcoded port number. The PORT environment variable is automatically set by App Service platform at startup time.  For example, for a Node.js Express app, you should have the following code as part of your server.js file. The full example can be found on [Github](https://github.com/Azure/app-service-quickstart-docker-images/tree/master/express-custom). 
~~~
app.listen(process.env.PORT); 
~~~
Note: we’re making continuous improvement to this VNet integration Preview feature for Linux web app, we will roll out feature improvements in the next few months.

