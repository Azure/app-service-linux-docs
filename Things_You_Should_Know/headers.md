## Headers on Azure App Service

  
### client-ip
The client-ip header is added on the Front End role as part of routing.  App Service will overwrite any existing header so they cannot be spoofed for a different IP address.

### server headers
- For Linux apps, the server header is suppressed by default.  However, if the application code adds the server header information, it will be passed along.
- For Windows apps, the header information is dependent on what the application code returns.
