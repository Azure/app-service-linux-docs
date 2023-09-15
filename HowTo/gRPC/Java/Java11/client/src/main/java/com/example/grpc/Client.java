package com.example.grpc;

import io.grpc.*;

public class Client
{
    public static void main( String[] args ) throws Exception
    {
      // Channel is the abstraction to connect to a service endpoint
      // Let's use plaintext communication because we don't have certs
      // final ManagedChannel channel = ManagedChannelBuilder.forTarget("localhost:8585")
      //   .usePlaintext(true)
      //   .build();

      final ManagedChannel channel = ManagedChannelBuilder.forTarget("jefmarti-java-11-grpc.azurewebsites.net")
        .usePlaintext(true)
        .build();

      // It is up to the client to determine whether to block the call
      // Here we create a blocking stub, but an async stub,
      // or an async stub with Future are always possible.
      GreetingServiceGrpc.GreetingServiceBlockingStub stub = GreetingServiceGrpc.newBlockingStub(channel);
      GreetingServiceOuterClass.HelloRequest request =
        GreetingServiceOuterClass.HelloRequest.newBuilder()
          .setName("you")
          .build();

      // Finally, make the call using the stub
      GreetingServiceOuterClass.HelloResponse response = 
        stub.greeting(request);

      System.out.println(response);
      System.out.println("grpc server responded");

      // A Channel should be shutdown before stopping the process.
      channel.shutdownNow();
    }
}
