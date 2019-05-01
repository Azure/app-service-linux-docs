## How does Multi-container Web App Determine Which Container is the "Web Container"

As Linux App Service only exposes a single (web) container to the world through the public endpoint, for Multi-container Web App, we use the following specific logic to determine which container is the "web" container:
1. If your YAML file has only one container in it, we'll use that container as the web container
2. If you have set the WEBSITES_WEB_CONTAINER_NAME app setting, we will use that as the web container
3. We will pick the first container in your YAML file that exposes either port 80 or port 8080 as host port
4. If we make it this far and we haven't picked the web container, we'll use the first container in the list of containers in your YAML file

