package com.example.grpc;

import io.grpc.*;

public class Client
{
    public static void main( String[] args ) throws Exception
    {
        
      // local dev
      // final ManagedChannel channel = ManagedChannelBuilder.forTarget("localhost:8585")
      //   .usePlaintext(true)
      //   .build();

      final ManagedChannel channel = ManagedChannelBuilder.forTarget("<your-app-name>.azurewebsites.net")
        .usePlaintext(true)
        .build();

      GreetingServiceGrpc.GreetingServiceBlockingStub stub = GreetingServiceGrpc.newBlockingStub(channel);
      GreetingServiceOuterClass.HelloRequest request =
        GreetingServiceOuterClass.HelloRequest.newBuilder()
          .setName("you")
          .build();

      GreetingServiceOuterClass.HelloResponse response = 
        stub.greeting(request);
        
      System.out.println(response);
      System.out.println("grpc server responded");

      channel.shutdownNow();
    }
}
