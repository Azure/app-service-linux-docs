
## Kestrel + YARP on Azure App Service

App Service has made a recent transition from using IIS/ARR for its FrontEndRole to using [Kestrel + YARP](https://techcommunity.microsoft.com/t5/apps-on-azure-blog/a-heavy-lift-bringing-kestrel-yarp-to-azure-app-services/ba-p/3607417).  The original FrontEndRole consisted of IIS running on HTTP.sys, and AAR to do the request forwarding using WinHTTP.  The new front end consist of Kestrel a fast webserver implementation and YARP, a reverse proxy toolkit that enables more customization and support for modern protocols like HTTP/2 and HTTP/3.  However, such a transition does come with some behavior changes as they handle incoming requests differently.   


### Client Disconnects
Previously with IIS/AntRR, client disconnects did not reach the workers.  Since client disconnects did not reach the workers, the workers would always respond with 200 OK response codes.  Now due to the nature of  Kestrel + YARP, the behavior has changed and the client disconnects are now passed through to the workers.  This change in behavior allows the worker to respond to client disconnects directly and may cause an increase in 499 status codes.

