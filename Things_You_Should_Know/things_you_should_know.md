# Things you should know: Web Apps on Linux

Azure App Service on Linux supports 2 scenarios:

- Bring your own **CODE**
- Bring your own **CONTAINER**

For **CODE** scenarios, App Service provides a base container that is maintained by the platform. This container targets a specific development framework (.NET Core, PHP, Node, etc...) and a specific version of that framework (.NET Core 3.0, .NET Core 3.1, etc...).

For **CONTAINER** scenarios, App Service provides a host where a custom container provided by the customer can execute.

In both scenarios, a set of App Service features are exposed through the ARM API as well as through the Azure Portal and Azure CLI / Powershell experience.

## General Information

### You can requests features to the App Service team

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

Azure App Service has a [Feedback forum](http://aka.ms/webapps-uservoice), here you can request new features and voted on them for priority. Please make sure to put "[Linux]" in the title so that we'll know it applies to App Service on Linux.

## Deployment

### Web Deploy

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ⛔          |

If you're deploying using Web Deploy, set `WEBSITES_WEBDEPLOY_USE_SCM` to false.

You can use Visual Studio to deploy to App Service using Web Deploy. However, when you do, you want to make sure that the endpoint for deployment isn't the Kudu container. To configure that, add an app setting to your app with a name of WEBSITES_WEBDEPLOY_USE_SCM and set the value to false.

### To prevent down-time when you update your code, use Continuous Deployment

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

If you update your code, push a new Docker image, and then restart your site manually to pick up that change, you're going to experience some down-time while App Service pulls the new image and start your container. You can avoid that by using the Continuous Deployment feature.

When you use Continuous Deployment, any time you push a new Docker image to your registry, Web App for Containers will pick up that change automatically. We'll pull the image and start the container, and we'll wait until that new container is running and ready for HTTP requests before we switch over to it. During that time, your old image will continue to serve requests into your app.

For more information on [Continuous Deployment](https://docs.microsoft.com/azure/app-service/containers/app-service-linux-ci-cd), see our documentation on it.

### If you change your Docker container, it may take a minute or so for it to take effect

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

If you change your Docker container settings to point to a new container and then click Save, it may take a minute or so before you'll see the new container when you browse to your site. While the new container is being pulled and started, we will continue to serve requests to your site using the old container. Only when the new container is started and ready to receive requests will we start sending requests to it.

A good way to tell if your new site is up and running is to the check the "site up time" for the Kudu (Advanced Tools) site as shown below. When the new container is up and running, the Kudu site will restart. If you see that the Kudu site has restarted, your new container should be ready.

### Custom images are stored on disk unless a worker change happens.

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

The first time you use a custom Docker image, we will do a "docker pull" and pull all layers. These layers are stored on disk just as if you were using Docker on-premise. When we do a "docker pull" after a site restart, we will only pull layers that have changed. If there have been no changes, we will simply use existing layers on disk.

If you change workers for any reason, however, we will have to pull down all layers again. Your worker will change if you scale up/down or if you scale out to add additional workers. There are also rare cases where your worker may change without a scale operation, but these cases are uncommon.

### Continuous Deployment requires that the image:tag combination remain the same.

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

Docker containers in Web App for Containers are specified using an image:tag combination. Therefore, if you configure Continuous Deployment, you'll need to ensure that any updates to your Docker image don't change the tag.

We've seen quite a few cases where customers will initially tag the image with a "v1" tag and enable CI. At some later time, they update the image and tag the new image with "v2" and then wonder why CI isn't working. Once you change the tag on an image, it's considered a different image from the initially configured image, and that will cause CI to not pick up the changes.

Note: If you don't specify a tag, Docker will look for an image with a tag called "latest". Therefore, if your configuration doesn't explicitly use a tag and someone tags your image with anything other than "latest", it will break continuous deployment.

## Configuration

### You can enable and disable storage persistence with an app setting

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

You can use an app setting called `WEBSITES_ENABLE_APP_SERVICE_STORAGE` to control whether or not the `/home` directory of your app is mapped to **App Service** built in storage.

Storage persistence can be a useful feature if you need to share information across instances (for scale up / scale out scenarios), or if you need information to persist across application restarts. However there are a few caveats to keep in mind:

If '/home' directory is mapped to **App Service** built in storage, your application will restart when a storage fail-over occurs.

If you don't require file persistence, you can set this app setting to **false**. this will make your app resilient to storage failovers.

The absence of this app setting will result in the setting being **"true"**. In other words, if this app setting does not exist for your app storage will be mounted.

[**Kudu** (Advanced Tools)](https://github.com/projectkudu/kudu/wiki) for Linux Apps runs in a separate container. The **Kudu** container always maps the /home directory to the App Service built in storage.  That way, the `/home/LogFiles` directory will persist between restarts and scale out operations in the **Kudu** container.

Therefore, if you need to get Docker logs or other logs, always use the **Kudu** Bash console instead of using SSH to access your app's container. (See this for more information on how to get the latest Docker logs from Kudu.)

> **Note:**
> 
> **Bring your own Code** apps ignore this app setting and always mount the built in storage.
 

### You cannot change permissions on the /home directory when persisting storage

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

When you persist storage with the WEBSITES_ENABLE_APP_SERVICE_STORAGE app setting, we mount a location in Azure Storage to the /home mount point. The permissions on this are 777. You cannot change these permissions, even if you attempt to do so from an initialization script or from SSH.

### App Settings are injected into your app as environment variables at runtime

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

If you need to set an environment variable for your application, simply add an App Setting in the Azure portal. When your app runs, we will inject the app setting into the process as an environment variable automatically.


### Some characters may be stripped out of environment variables names

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

We allow only alpha-numeric characters and the underscore character for an App Setting's name. (The value can contain special characters.) Any other characters will be stripped from the App Setting name (and, therefore, the environment variable name) at runtime. We also provide this information in our FAQ.

### Your environment variables won't appear in the Bash console

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

If you use the Bash console in Advanced Tools (Kudu) to look at environment variables, you won't see environment variables that you set using App Settings. That's because the Bash console runs in a separate context from your Web App. In order to see your environment variables, use the Environment page in Advanced Tools or use code to retrieve the environment variables.

### Set your default document in a Node.js app using JavaScript

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

When you create a Node.js app, by default, it's going to use `hostingstart.html` as the default document unless you configure it to look for a different file. You can use a JavaScript file to configure your default document. Create a file called index.js in the root folder of your site and add the following content.

``` Node
var express = require('express');
var server = express();
var options = {
index: 'index.html'
};
server.use('/', express.static('/home/site/wwwroot', options));
server.listen(process.env.PORT);
```

This will configure index.html as the default document for your app.


### You can now force SSL using the "HTTPS Only" option in the Azure portal

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

We've now added the ability to force SSL traffic using the "HTTPS Only" option in the Azure portal. For details on how to do that, see our documentation.

### If you're persisting files, only the /home directory is persisted

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

By default, we don't persist files in your site. However, if you need to persist files, you can enable App Service Storage (see "You can enable and disable storage persistence with an app setting"). If you enable this, we mount the /home directory to Azure Storage. If your app is restarted, any files saved within the /home directory and sub-directories will persist. However, any files or directories outside of the /home directory will not be persisted between site recycles. This can impact you in a couple of different ways.

If you use npm, apt, or similar to install something from the console after your app starts, once the app restarts, whatever you installed will be gone.
If you save files outside of the /home directory, if your app restarts, those files will be gone.
If you need an extension or other component for your app to run, make sure that you install it via your Dockerfile. That way, it will be available always. If you need to persist files that your app is creating, make sure that you write them into the /home directory structure.

For more information on creating your own container for use with Web App for Containers, see our documentation.

### To use SSH, your Docker image needs special sauce

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

We provide the ability to SSH into your app, but if you're using a custom container, you need to take additional steps in order to add this ability to your app. We've provided all the steps necessary here.

### To use SFTP, your Docker image needs more special sauce

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

Once you create a TCP tunnel to Azure App Service from your development machine, you can connect to your Web App using SFTP. However, if you are using Web App for Containers, your Docker image needs some special configuration for this to work. Specifically, the SFTP subsystem must be specified in the sshd_config file. (The sshd_config file is added to your app when you follow the directions here for enabling SSH into a custom container.)

To use SFTP, make sure the following line is in your sshd_config file.

`subsystem sftp internal-sftp`

This will enable you to successfully transfer files using SFTP.

### You can use your favorite SSH client with Web Apps

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

You can use any SSH client you want with Web Apps. Whether you're a Windows user, a macOS user, or a Linux user, you can easily SSH into your Web App. For all of the details on doing that, see our "Things You Should Know: Web Apps and SSH" article.

### Don't worry about the SSH port in App Service

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

We use port `2222` for SSH into your app's container, but that doesn't mean that port `2222` is exposed over the Internet. No matter how you use SSH in your app, all SSH traffic is handled through an endpoint on port `443`. If you're not using SSH, you don't have to worry about closing port 2222 because it's not exposed to the Internet.

### Pay attention to your slash direction

Applies to Web App for Containers
When specifying your image running in Docker Hub, make sure that you pay attention to your slash. Don't use a backslash because that won't work. You should separate the username and image name using a front slash (/).

### You can use your own DNS servers

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

Some customers want to use their own DNS servers within their containers. Configuring this is relatively simple using an initialization script. If you've followed our guidance on enabling SSH for your custom container, you should already have your container configured to use an initialization script. To use your own DNS servers, you simply need to include the following line in your initialization script.


`echo "nameserver #.#.#.#" > /etc/resolv.conf`

If you want to use multiple nameservers, you can do that with this code.

`echo "nameserver #.#.#.#" > /etc/resolv.conf && echo "nameserver #.#.#.#" >> /etc/resolv.conf`

Of course, replace "#.#.#.#" with the IP of the DNS nameserver you want to use.

## Troubleshooting

### If your app doesn't start, check the Docker log

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

**App Service** logs useful information into the Docker log that can help you troubleshoot your site when it doesn't start or if it's restarting. The service logs a lot more than you might be used to seeing in a Docker log, and we will continue to work on making this logging more useful.

There are several ways to access Docker logs:

- Docker logs appear on the Container Settings page in the portal. (These are truncated, but you can download them by clicking on the Download Logs button.)
- You can find the Docker log in the /LogFiles directory. You can access this via the Kudu (Advanced Tools) Bash console or by using an FTP client to access it.
- You can use our API to download the current logs. (see (You can discover and download the latest Docker logs using Kudu)[#You-can-discover-and-download-the-latest-Docker-logs-using-Kudu])
   - The naming convention for the Docker log is YYYY_MM_DD_RDxxxxxxxxxxxx_docker.log.

> **Note** 
>
> If you try and download the Docker log that is currently in use using an FTP client, you may get an error because of a file lock. 
>
> In that case, you can download it using our API (see (You can discover and download the latest Docker logs using Kudu)[#You-can-discover-and-download-the-latest-Docker-logs-using-Kudu]) or you can use "tail" in the console to view it. (Our API gets you the current Docker log, so if you want to review a past log, use the "tail" option.)

To view the Docker log using tail, access the console, switch into the LogFiles directory, and run this command:

`tail 2017_09_05_RD*0FA_docker.log`

In this example, I'm viewing the Docker log for September 5. Note that I'm also using a wildcard replacement for the machine ID (the RD number) so that I don't have to type all the characters.

> **Tip:** 
> 
> You can pipe the output of tail to a new file in case you want to download it. Simply append "> filename.txt" to the command above.

### You can discover and download the latest Docker logs using Kudu

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

App Service has an API that allows you to easily see the current Docker log details (such as the filename, etc.) and also download the current Docker logs in Zip format.

To see details on the current Docker logs in JSON format, you can use this URL:

`https://<yout-app-name>.scm.azurewebsites.net/api/logs/docker`

You can get to this easily by going to **Kudu** (Advanced Tools) and then appending "/api/logs/docker" to the URL. The output of this will be a JSON response with the most relevant and current Docker logs.

If you want to download the logs shown in the above API in Zip format, append "zip" to the URL. For example:

`https://<yout-app-name>.scm.azurewebsites.net/api/logs/docker/zip`


### You can view the most recent entries in your Docker log in the Azure portal

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

To make it easier to see what's going on with your Docker container, we show you the latest entries in the Docker log in the Azure portal. Simply click on **Container Settings** in the portal menu and you'll see the Docker log.

You can click the Copy button to copy the Docker log. You can also download the full Docker log by clicking on Download Logs.

### If your container takes a long time to start, increase the start time limit

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

**App Service** will wait 230 seconds for a container to start, initialize and respond to an HTTP request. **App Service** interprets this first response to an HTTP request as an idication that your app has initialized and is ready to recive further requests. If the timout of 230 seconds is reached with no response from the app, then it's considerd a failure to start. 

Some containers might need more than 230 seconds to start, the default timeout can be overridden through the `WEBSITES_CONTAINER_START_TIME_LIMIT` app setting. This app setting can be set to a maximum of 1800 seconds.

### Your container must respond to an HTTP ping

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

App Service will a certain amount of time for your container to start before we consider it be a failed start. In order for App Service to consider a container to be successfully started, the container must start and it must respond to an HTTP ping. If the container starts but does not respond to a ping, we will eventually log an event in the Docker log saying that it didn't start.

Here's a snippet from a Docker log that illustrates the problem. 

``` log
2017-09-14 19:26:22.494 INFO  - Starting container for site
2017-09-14 19:26:22.496 INFO  - docker run -d -p 52879:80 --name customer-webapp . . .
. . .
2017-09-14T19:26:34.628607412Z { engine: 'joenode', port: '3000', pid: 5 }
2017-09-14 19:30:14.428 ERROR - Container customer-webapp_0 for site customer-webapp did not start within expected time limit. Elapsed time = 230.0443067 sec>
```

I have truncated much of this output, but what you can see here is that 

The log output shows the "docker run" command was run with no error messages. However, at the end of the log, we see a message that the container did not start within the expected time limit.

Notice in the next to the last line that the Node.js engine is listening on port `3000`. The problem here is that port `3000` was never exposed, so when we attempt to ping the container, we aren't pinging on a port on which the container is listening. There are a couple of ways to resolve this.

Use the `EXPOSE` instruction in your Dockerfile to expose port `3000`.
Use the `WEBSITES_PORT` app setting with a value of "3000" to expose that port.

### You can remotely debug your Node.js app using VS Code

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

If you're a *Node.js* developer, you can remotely debug your Web App using VS Code. You can set breakpoints, step through code, etc. on your Web App running in App Service from your development machine. For all of the details on how to remotely debug, check out [this blog post](https://medium.com/@auchenberg/introducing-remote-debugging-of-node-js-apps-on-azure-app-service-from-vs-code-in-public-preview-9b8d83a6e1f0) from Kenneth Auchenberg on the VS Code team.

## Best Practices

### You shouldn't install components using SSH because they won't persist

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

You can **SSH** into your app container and install components. However, when your site is restarted, anything that you install will be gone. Why is that? That's the way Docker works. When your site starts, we run your Docker image and create a Docker container. Your app runs inside of that container, and the file system contains only what is in the Docker image. If your Docker image doesn't install a particular component, it won't be there when your container starts.

If you want to install a particular component, make sure that you do it in a Dockerfile so that the component is included in your Docker image. See [this documentation](https://docs.microsoft.com/azure/app-service/containers/tutorial-custom-docker-image) for full information on how to do that.

### The Bash console in Kudu (Advanced Tools) is a different container

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

We offer a **BASH** console in [Kudu (Advanced Tools)](https://github.com/projectkudu/kudu/wiki) that you can use to browse directory structure, etc. It's important to realize that this console is running inside of the **Kudu** container. This is not the same container that your app is running in, so if you look at files and directories here, they won't reflect your app. The only exception to that is the /home directory. That directory is, by default, mounted from App Service built in storage, and it's the same location in both the **Kudu** container and your app's container. [Learn more about persistent storage](#You-can-enable-and-disable-storage-persistence-with-an-app-setting)

### You don't need (and should not have) SSL/TLS support in your app

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

**App Service** terminates SSL/TLS at the front-ends. That means that SSL/TLS requests never get to your app. That's good news for you because it means that you don't need to (and should not) implement any support for SSL/TLS into your app. Also as stated above, it's important to understand that the front-ends where SSL/TLS is terminated are inside of our Azure data centers. If you use SSL/TLS with your app, your traffic across the Internet will always be safely encrypted.

### You can only expose one port to the outside world

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ⛔    | ✅          |

**Container** apps allow you to expose only one port to the outside world. That means that your container can only listen for HTTP/HTTPS requests on a single port. Some apps need multiple ports. For example, you might have one port that is used for requests into the app and a separate port that is used for a dashboard or admin portal. As of today, that configuration isn't possible in Web App for Containers.

We will attempt to detect which port to bind to your container, but you can also use the `WEBSITES_PORT` app setting and configure it with a value for the port you want to bind to your container.

> **Note**
>
> **Bring your own Code** apps use port `80` and `443` by default and can't be configured to use alternate ports.

### Don't use df to find your disk space usage

|**CODE**|**CONTAINER**|
|:------:|:-----------:|
| ✅    | ✅          |

You're probably used to using `df` to find out disk space in your volumes. You can certainly do that in App Service, but what you'll see isn't really going to be as helpful as you might think.

Assuming you are persisting files in the /home directory (which is currently the default), you will have a quota based on your pricing tier. However, if you use `df`, the disk space you see **won't reflect that quota**. If you want to find out your disk usage, use **Quotas** in your Web App's menu, **File System Storage** in the App Service Plan's menu, or use the REST API to find your usage.
