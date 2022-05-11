If you'd like to run your Ruby on Rails workloads in a container you can do so by using a [custom container]() The following is a tutorial on how to run your Ruby on Rails application in a container on App Service.

#### Prerequisite 
1. Ruby on Rails application
2. Docker

#### Step 1: Add Dockerfile
The first thing you'll need to containerize your Ruby application is to add a Dockerfile.  This file will contain the instructions necessary for Docker to build your container.

1. Go to your application code and add a new file named `Dockerfile`.  This file can be placed next to your Gemfile.
2. Next, paste the following code:
```dockerfile 
FROM ruby:2.7.6 
WORKDIR /usr/src/app 
COPY Gemfile Gemfile.lock ./ 
RUN bundle install 
ADD . /usr/src/app/ 
EXPOSE 3000 
CMD rails s -b 0.0.0.0
```

#### Step 2: Build and Run local container
Now that we've added our Dockerfile to the application, we can build the container and run it locally.
1. Open up your terminal and navigate to the applications folder where the Dockerfile lives
2. Run the following command to build and name the docker image.
```
docker build -t my-ruby-docker-image .
```
3. Next, run the Docker run command to run it locally
```
docker run -it -p 3000:3000 my-ruby-docker-image
```

Once you run this command, your docker image will run at the port we specified.  You can visit https://localhost:3000 and view your application. 

#### Step 3: Tag and Push the Docker image to Azure Container Registry
Now that our container is working locally, we can confidently deploy our application to Azure Container Registry.
1. Use the docker `docker tag` command to tag your local image to your registry

```
docker tag my-ruby-docker-image:latest <my-registry-name>.azurecr.io/my-ruby-docker-image
```
2. Next, use the docker `docker push` command to push the image to Azure Container Registry
```
docker push <my-registry-name>.azurecr.io/my-ruby-docker-image
```

Once your image is pushed, you are now ready to create a new web app in App Service.

#### Step 4: Deploy to App Service
The last step is to create a Web App specifically for container workloads
1. Create a Web App resource as you normally would
2. For the instance details choose the following options:
	1. Publish: Docker Container
	2. Operating System: Linux
3. Then, click the Next:Docker > button at the bottom of the page
4. Find the Image Source drop-down menu and choose Azure Container Registry
5. Choose your registry options to match the container you pushed to ACR.
6. Click Review+Create to start deploying your application

Once the resource is created, wait a few minutes as the container is building and in a short time you will see your application deployed in a custom container.