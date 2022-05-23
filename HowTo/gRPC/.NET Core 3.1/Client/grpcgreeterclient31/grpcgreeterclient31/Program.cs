using System;
using System.Net.Http;
using Grpc.Net.Client;
using grpcgreeterclient31;


// The port number must match the port of the gRPC server.
using var channel = GrpcChannel.ForAddress("http://localhost:8282");
var client = new Greeter.GreeterClient(channel);
var reply = await client.SayHelloAsync(
                  new HelloRequest { Name = "GreeterClient" });
Console.WriteLine("Greeting: " + reply.Message);
Console.WriteLine("Press any key to exit...");
Console.ReadKey();
