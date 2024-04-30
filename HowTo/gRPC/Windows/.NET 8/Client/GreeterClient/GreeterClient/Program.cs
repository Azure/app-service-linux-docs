using System.Threading.Tasks;
using Grpc.Core;
using Grpc.Net.Client;
using GreeterClient;


/// Create gRPC client
using var channel = GrpcChannel.ForAddress($"https://your-app-name.azurewebsites.net/");
var client = new Greeter.GreeterClient(channel);

Console.WriteLine("Press any key to START");
Console.ReadKey();
Console.WriteLine();

/// UNARY CALL
Console.WriteLine("Unary call (request, response)");
Console.ReadKey();
var reply = await client.SayHelloAsync(new HelloRequest { Name = "everyone!" });
Console.WriteLine("Message: " + reply.Message);

Console.WriteLine();
Console.WriteLine("Press any key to CONTINUE");
Console.ReadKey();
Console.WriteLine();

/// SERVER STREAM
Console.WriteLine("Server Streaming (One request, many responses): ");
Console.ReadKey();
using var serverReply = client.SayHelloStream(new HelloRequest { Name = " 1, 2, 3, 4, 5, 6, 7" });

await foreach (var response in serverReply.ResponseStream.ReadAllAsync())
{
    Console.WriteLine("Message: " + response.Message);
}

Console.WriteLine();
Console.WriteLine("Press any key to CONTINUE");
Console.ReadKey();
Console.WriteLine();

/// CLIENT STREAM
Console.WriteLine("Client Streaming (Many requests, one response): ");
Console.ReadKey();
using (var streamingcall = client.SayHelloStreamClient())
{
    foreach (var name in new[] { "Byron", "Jeff", "Jordan", "Denver", "Stefan", "Yutang" })
    {
        await streamingcall.RequestStream.WriteAsync(new HelloRequest()
        {
            Name = name
        });

        await Task.Delay(TimeSpan.FromSeconds(1));
    }

    await streamingcall.RequestStream.CompleteAsync();
    var response = await streamingcall;
    Console.WriteLine(response.Message);
}

Console.WriteLine();
Console.WriteLine("Press any key to CONTINUE");
Console.ReadKey();
Console.WriteLine();


/// BIDIRECTIONAL
Console.WriteLine("Bidirectional (Many requests, many responses)");
Console.ReadKey();
var cts2 = new CancellationTokenSource(TimeSpan.FromMinutes(10));
using (var streamingCall = client.SayHelloBidirectional())
{
    var t = Task.Run(async () =>
    {
        try
        {
            await foreach (var greeting in streamingCall.ResponseStream.ReadAllAsync(cancellationToken: cts2.Token))
            {
                Console.WriteLine(greeting.Message);
            }
        }
        catch (RpcException ex) when (ex.StatusCode == StatusCode.Cancelled)
        {
            Console.WriteLine("Stream cancelled");
            Console.WriteLine(ex.ToString());
        }
        catch (Exception ex)
        {
            Console.WriteLine(ex.ToString());
        }
    });

    foreach (var name in new[] { "Byron", "Jeff", "Jordan", "Denver", "Stefan", "Yutang" })
    {
        await streamingCall.RequestStream.WriteAsync(new HelloRequest()
        {
            Name = name
        });

        await Task.Delay(1000);
    }

    await streamingCall.RequestStream.CompleteAsync();
    await t;
}

Console.WriteLine();
Console.WriteLine("Press any key to EXIT");
Console.ReadKey();
Console.WriteLine();