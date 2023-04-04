using System.Threading.Tasks;
using Grpc.Core;
using Grpc.Net.Client;
using GrpcServerStreamClient;


// SERVER STREAM
using var channel = GrpcChannel.ForAddress("https://grpcserverstream.azurewebsites.net/");

var client = new Greeter.GreeterClient(channel);

var cancelToken = new CancellationTokenSource(TimeSpan.FromMinutes(5));

using (var call = client.SayHello(new HelloRequest { Name = " 1, 2, 3, 4, 5, 6, 7, 8, 9, 10" }))
{
    try
    {
        await foreach (var response in call.ResponseStream.ReadAllAsync(cancellationToken: cancelToken.Token))
        {
            Console.WriteLine(response.Message);
        }
    }
    catch (RpcException ex) when (ex.StatusCode == StatusCode.Cancelled)
    {
        Console.WriteLine("Stream Cancelled");
    }

    Console.WriteLine("Press any key to exit...");
    Console.ReadKey();
};
