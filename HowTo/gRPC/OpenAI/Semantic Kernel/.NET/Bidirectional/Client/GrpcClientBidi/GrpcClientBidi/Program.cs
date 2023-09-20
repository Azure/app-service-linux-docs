using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using Grpc.Core;
using Grpc.Net.Client;
using GrpcClientBidi;

using var channel = GrpcChannel.ForAddress("https://<your-app-name>.azurewebsites.net/");


/// Unary Call ///
var clientUnary = new Greeter.GreeterClient(channel);

Console.ForegroundColor = ConsoleColor.DarkGreen;
Console.WriteLine("Enter input data to gRPC server:");
Console.ForegroundColor = ConsoleColor.White;
var InputText = $@"{Console.ReadLine()}";
var reply = await clientUnary.UnaryCallAsync(
                  new DataRequest { Data = InputText });

/// Bi-directional call ///
var client = new Greeter.GreeterClient(channel);
var cts2 = new CancellationTokenSource(TimeSpan.FromMinutes(10));

while (true)
{
    Console.WriteLine();
    Console.ForegroundColor = ConsoleColor.DarkGreen;
    Console.WriteLine("Enter query request to gRPC server (Press ENTER to quit):");
    Console.ForegroundColor = ConsoleColor.White;
    var text = @"{{$input}}" + Console.ReadLine();
    if (text == @"{{$input}}") { break; }

    Console.WriteLine();

    using (var streamingCall = client.SayHelloBidirectional())
    {
        var t = Task.Run(async () =>
        {
            try
            {
                await foreach (var greeting in streamingCall.ResponseStream.ReadAllAsync(cancellationToken: cts2.Token))
                {
                    // write message from server 
                    Console.ForegroundColor = ConsoleColor.Gray;
                    Console.WriteLine("Server Response: " + greeting.Message);
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

        foreach (var name in new[] { text })
        {
            await streamingCall.RequestStream.WriteAsync(new HelloRequest()
            {
                Name = name
            });

            await Task.Delay(3000);


        }

        await streamingCall.RequestStream.CompleteAsync();
        await t;
    }


}
