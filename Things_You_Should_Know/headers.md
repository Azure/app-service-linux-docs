## Headers on Azure App Service

  
### client-ip
The client-ip header is added on the Front End role as part of routing.  App Service will overwrite any existing header so they cannot be spoofed for a different IP address.
