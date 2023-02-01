# How-to deploy a Go gRPC app on App Service

> [!WARNING]
> gRPC is currently available to try as a Public Preview feature. Go is available as Expermental Release.

gRPC is a Remote Procedure Call framework that is used to streamline messages between your client and server over HTTP/2.  Using gRPC protocol over HTTP/2 enables the use of features like multiplexing to send multiple parallel requests over the same connection and bi-directional streaming for sending requests and responses simultaneously.  

The following is a tutorial on how to deploy a Go gRPC application on App Service. 

#### Prerequisite
In this tutorial, we'll be deploying a gRPC server to App Service and making a gRPC request to the deployed server from a local gRPC client.  If you have not created a gRPC client and server yet, please follow this [Go Quick Start](https://grpc.io/docs/languages/go/quickstart/) to do so.  

The following tutorial builds from the created gRPC client and server in that documentation.  If you already have a gRPC client and server, you may use these steps to add to existing Go apps as well.  This tutorial will work for both Go 1.18 and Go 1.19.

### Setup the gRPC Server app
In order to prepare our gRPC server application to deploy to App Service, we will need to configure the Go app with an additional port so that the system can ping the application for Healthcheck requests.

In your **main.go** add the following code to configure the extra port.  

```Go
// Configure Go to listen Healthcheck requests 
func async[T any](f func() T) chan T {
    ch := make(chan T)
    go func() {
        ch <- f()
    }()
    return ch
}

func HttpServer() {
	http.HandleFunc("/", HelloServer)
	http.ListenAndServe(":8080", nil)
}

func main() {
    async(func() string {
		HttpServer()
		return "1"
    })
.....
}

```

Once configured this will ensure that your application is listening to a specific HTTP only port, which will be needed when we deploy to App Service. 

This is the code of your completed **main.go**.

```Go
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"net/http"
	"google.golang.org/grpc"
	pb "helloworld/helloworld"
)

var (
	port = flag.Int("port", 50051, "The server port")
)

// server is used to implement helloworld.GreeterServer.
type server struct {
	pb.UnimplementedGreeterServer
}

// SayHello implements helloworld.GreeterServer
func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	log.Printf("Received: %v", in.GetName())
	return &pb.HelloReply{Message: "Hello " + in.GetName()}, nil
}

func HelloServer(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello World")
}

func async[T any](f func() T) chan T {
    ch := make(chan T)
    go func() {
        ch <- f()
    }()
    return ch
}

func HttpServer() {
	http.HandleFunc("/", HelloServer)
	http.ListenAndServe(":8080", nil)
}

func main() {
    async(func() string {
		HttpServer()
		return "1"
    })
	flag.Parse()
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterGreeterServer(s, &server{})
	log.Printf("server listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}


```
You can run your code locally to ensure that it works. Once this is done your application is now ready to deploy to App Service.

### Deploy to App Service
Now that you have your server application setup and running locally, you can go to the portal and create your web app.  One thing to note is that Go and gRPC is currently only supported on Linux so be sure to choose this option when creating your web app.

Create your web app as you normally would.  Choose **Code** as your Publish option.  Choose **Go 1.18 (Experimental)** or **Go 1.19 (Experimental)** as your Runtime stack and **Linux** as your Operating System.  

Now that your web app is created, you'll need to do the following before deploying your application:

#### 1. Set HTTP version
The first setting you'll need to configure is the HTTP version
1. Navigate to **Configuration** under **Settings** in the left pane of your web app
2. Click on the **General Settings** tab and scroll down to **Platform settings**
3. Go to the **HTTP version** drop-down and select **2.0**
4. Click **save**

This will restart your application and configure the front end to allow clients to make HTTP/2 calls.

#### 2. Enable HTTP 2.0 Proxy
Next, you'll need to configure the HTTP 2.0 Proxy:
1. Under the same **Platform settings** section, find the **HTTP 2.0 Proxy** setting and switch it to **On**.
2. Click **save**

Once turned on, this setting will configure your site to be forwarded HTTP/2 requests.

#### 3. Add HTTP20_ONLY_PORT application setting
Earlier, we configured the application to listen to a specific gRPC port.  Here we'll add an app setting HTTP20_ONLY_PORT and put the value as the port number we used earlier.
1. Navigate to the **Configuration** under **Settings** on the left pane of your web app.  
2. Under **Application Settings**, click on **New application setting**
3. Add the following app setting to your application
	1. **Name =** HTTP20_ONLY_PORT 
	2. **Value =** 50051

This setting will to communicate with the application on this port for all gRPC requests.

### Publish your code
You can deploy your code using any of the several methods provided by Azure App Service like GitHub Actions, Deploy Zip, Deploy from Local Git or Azure Pipelines. Choose the option that works best for you. 

For the purpose of this tutorial, you can use Local Git for your deployment [Local Git deployment to Azure App Service](https://learn.microsoft.com/en-us/azure/app-service/deploy-local-git) 

### Confirm a gRPC request call from your local client
Now that the gRPC service is deployed and we have a URL, we can make a call from our local client to test that our channel connects to the server and that our client can receive a response.

You can use the sample client from here [Go Quick Start](https://grpc.io/docs/languages/go/quickstart/)

Navigate to the **greeter_client/main.go** file and swap out the localhost address for the App Service URL.  

> Note: gRPC calls must be over https.  Insecure calls are not possible.

```Go
// replace the localhost address with your App Service URL
var (
	addr = flag.String("addr", "mygogrpcapp.azurewebsites.net:443", "the address to connect to")
	name = flag.String("name", defaultName, "Name to greet")
)
```

You would also need to change your connection from insecure to TLS.

```Go
// Set up a connection to the server.
	
	config := &tls.Config{
        InsecureSkipVerify: true,
    }
    conn, err := grpc.Dial(*addr, grpc.WithTransportCredentials(credentials.NewTLS(config)))
	
	//conn, err := grpc.Dial(*addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
```

This is the code of your completed **greeter_client/main.go**.

```Go
package main

import (
	"context"
	"flag"
	"log"
	"time"

	"google.golang.org/grpc"
	pb "helloworld/helloworld"
	"google.golang.org/grpc/credentials"
	"crypto/tls"
)

const (
	defaultName = "world"
)

var (
	addr = flag.String("addr", "hellogo.azurewebsites.net:443", "the address to connect to")
	name = flag.String("name", defaultName, "Name to greet")
)

func main() {
	flag.Parse()
	// Set up a connection to the server.
	
	config := &tls.Config{
        InsecureSkipVerify: true,
    }
    conn, err := grpc.Dial(*addr, grpc.WithTransportCredentials(credentials.NewTLS(config)))
	
	//conn, err := grpc.Dial(*addr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	c := pb.NewGreeterClient(conn)

	// Contact the server and print out its response.
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	r, err := c.SayHello(ctx, &pb.HelloRequest{Name: *name})
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}
	log.Printf("Greeting: %s", r.GetMessage())
}
```

Now save your application and run the local client.  Your console application should receive and display the message from your gRPC service.  If you used the server from the tutorial, it will read the same message:

```Console
go run main.go --name=Azure
2023/01/31 19:59:51 Greeting: Hello Azure
```

The response from your deployed server will be shown using the updated channel.  If this is shown you have successfully deployed your gRPC server application to App Service.

#### Resources
[Go Quick Start](https://grpc.io/docs/languages/go/quickstart/)

