using System.Threading.Tasks;
using Grpc.Core;
using Grpc.Net.Client;
using GrpcServiceClient;


using var channel = GrpcChannel.ForAddress("https://grpcserviceapp.azurewebsites.net/");
var client = new Greeter.GreeterClient(channel);

var reply = await client.SayHelloAsync(
                  new HelloRequest { Name = ".NET Devs!" });

Console.WriteLine(reply.Message);
Console.WriteLine("Press any key to exit...");
Console.ReadKey();