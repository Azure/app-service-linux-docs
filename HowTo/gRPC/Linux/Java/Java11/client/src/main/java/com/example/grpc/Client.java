package com.example.grpc;

import io.grpc.*;
import io.grpc.stub.StreamObserver;

import com.example.grpc.GreetingServiceOuterClass.HelloRequest;
import com.example.grpc.GreetingServiceOuterClass.HelloReply;

import java.util.logging.Logger;
import java.sql.Time;
import java.util.Iterator;
import java.util.List;
import java.util.logging.Level;
import java.util.concurrent.CountDownLatch;

public class Client
{
    private static final Logger logger = Logger.getLogger(Client.class.getName());

    private static void info(String message) {
        logger.log(Level.INFO, message);
    }

    private static void error(String message) {
        logger.log(Level.SEVERE, message);
    }

    public static void main( String[] args ) throws Exception
    {
        
      // Local Development
      final ManagedChannel channel = ManagedChannelBuilder.forTarget("localhost:8585")
        .usePlaintext()
        .build();

      // Prod Environment
      // final ManagedChannel channel = ManagedChannelBuilder.forTarget("<your-app-name>.azurewebsites.net")
      //   .build();

      // Create gRPC stubs
      GreetingServiceGrpc.GreetingServiceBlockingStub blockingStub = GreetingServiceGrpc.newBlockingStub(channel);
      GreetingServiceGrpc.GreetingServiceStub asyncStub = GreetingServiceGrpc.newStub(channel);

      System.out.println("grpc client started");
      System.out.println("");
      
      
      System.out.println("Press any key to START");
      System.in.read();
      System.out.println("");

      /// UNARY CALL 
      System.out.println("Unary call (request, response)");
      System.in.read();
      Thread.sleep(1000);

      HelloRequest unaryRequest =
        HelloRequest.newBuilder()
          .setName("everyone!")
          .build();

      HelloReply response;

      // Call the method on the server
      response = blockingStub.sayHello(unaryRequest);

      // Log the response from the method
      System.out.println("Message: " + response.getMessage());
        

      System.out.println("");
      System.out.println("Press any key to CONTINUE");
      System.in.read();
      System.out.println("");

      /// SERVER STREAMING
      System.out.println("Server streaming (one request, many responses)");
      System.in.read();
      Thread.sleep(1000);
    
      HelloRequest reqServerStream = HelloRequest.newBuilder()
      .setName("Hello")
      .build();

      Iterator<HelloReply> replies;
      
      try {
        replies = blockingStub.sayHelloStream(reqServerStream);
        
        while (replies.hasNext()) {
          HelloReply reply = replies.next();
          System.out.println("Message: " + reply.getMessage());
          Thread.sleep(1000);
        }
      } catch (StatusRuntimeException e) {
        System.out.println("RPC failed: " + e.getStatus());
      }

      System.out.println("");
      System.out.println("Press any key to CONTINUE");
      System.in.read();
      System.out.println("");


      /// CLIENT STREAMING
      System.out.println("Client streaming (Many requests, one response)");
      System.in.read();
      Thread.sleep(1000);
  
      List<HelloRequest> requests = List.of(
        HelloRequest.newBuilder().setName("John").build(),
        HelloRequest.newBuilder().setName("Doe").build(),
        HelloRequest.newBuilder().setName("Smith").build()
      );

      final CountDownLatch finishLatch = new CountDownLatch(1);
      StreamObserver<HelloReply> responseObserver = new StreamObserver<HelloReply>() {
            @Override
            public void onNext(HelloReply response) {
              System.out.println("Response: " + response.getMessage());
            }
    
            @Override
            public void onError(Throwable t) {
              error("Error: " + Status.fromThrowable(t));
              finishLatch.countDown();
            }
    
            @Override
            public void onCompleted() {
              finishLatch.countDown();
            }
          };
        
    
      StreamObserver<HelloRequest> requestObserver = asyncStub.sayHelloStreamClient(responseObserver);
      try {
        for (HelloRequest request : requests) {
          System.out.println("Sending: " + request.getName());
          requestObserver.onNext(request);
          Thread.sleep(1000);
        }

        if (finishLatch.getCount() == 0) {
          // RPC completed or errored before we finished sending.
          // Sending further requests won't error, but they will just be thrown away.
          return;
        }
      } catch (RuntimeException e) {
        // Cancel RPC
        requestObserver.onError(e);
        throw e;
      }

      // Mark the end of requests
      requestObserver.onCompleted();

      // Receiving happens asynchronously
      finishLatch.await(1, java.util.concurrent.TimeUnit.MINUTES);
      
      System.out.println("Press any key to CONTINUE");
      System.in.read();
      System.out.println("");


      /// BIDIRECTIONAL STREAMING
      System.out.println("Bidirectional streaming (many requests, many responses)");
      System.in.read();
      Thread.sleep(1000);
      
      final CountDownLatch finishLatchBidi = new CountDownLatch(1);
      StreamObserver<HelloRequest> requestObserverBidi = asyncStub.sayHelloBidirectional(new StreamObserver<HelloRequest>() {
        @Override
        public void onNext(HelloRequest request) {
          System.out.println("Received: " + request.getName());
        }

        @Override
        public void onError(Throwable t) {
          error("Error: " + Status.fromThrowable(t));
          finishLatchBidi.countDown();
        }

        @Override
        public void onCompleted() {
          finishLatchBidi.countDown();
        }
      });

      try {
        HelloRequest[] requestsBidi = {
          HelloRequest.newBuilder().setName("John").build(),
          HelloRequest.newBuilder().setName("Doe").build(),
          HelloRequest.newBuilder().setName("Smith").build(),
          HelloRequest.newBuilder().setName("Bob").build()
        };

        for(HelloRequest request : requestsBidi) {
          System.out.println("Sending: " + request.getName());
          requestObserverBidi.onNext(request);
          Thread.sleep(1000);
        }
      } catch (RuntimeException e) {
        // Cancel RPC
        requestObserverBidi.onError(e);
        throw e;
      }

      // Mark the end of requests
      requestObserverBidi.onCompleted();

      // Receiving happens asynchronously
      finishLatchBidi.await(1, java.util.concurrent.TimeUnit.MINUTES);

      System.out.println("");
      System.out.println("Press any key to EXIT");
      System.in.read();
      System.out.println("");

      channel.shutdownNow();
    }
}
