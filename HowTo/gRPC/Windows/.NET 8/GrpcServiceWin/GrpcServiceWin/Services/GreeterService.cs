using Grpc.Core;
using GrpcServiceWin;
using System.Text;
using System.Threading.Channels;

namespace GrpcServiceWin.Services
{
    public class GreeterService : Greeter.GreeterBase
    {
        private readonly ILogger<GreeterService> _logger;
        public GreeterService(ILogger<GreeterService> logger)
        {
            _logger = logger;
        }

		/// UNARY STREAM
        public override Task<HelloReply> SayHello(HelloRequest request, ServerCallContext context)
        {
            return Task.FromResult(new HelloReply
            {
                Message = "Hello " + request.Name
            });
        }

		/// SERVER STREAM
		public override async Task SayHelloStream(HelloRequest request, IServerStreamWriter<HelloReply> responseStream, ServerCallContext context)
		{
			foreach (var name in request.Name.Split(","))
			{
				await responseStream.WriteAsync(new HelloReply()
				{
					Message = "#" + name
				});
				await Task.Delay(1000);
			}
		}

		/// CLIENT STREAM
		public override async Task<HelloReply> SayHelloStreamClient(IAsyncStreamReader<HelloRequest> requestStream, ServerCallContext context)
		{
			var inputNames = new List<string>();
			await foreach (var helloRequest in requestStream.ReadAllAsync())
			{
				inputNames.Add(helloRequest.Name);
			}

			var sb = new StringBuilder("Hello ");
			foreach (var name in inputNames)
			{
				sb.Append(name + ",");
			}
			sb.Length = sb.Length - 1;
			sb.Append("!");

			return new HelloReply()
			{
				Message = sb.ToString()
			};
		}

		/// BIDIRECTIONAL STREAM
		public override async Task SayHelloBidirectional(IAsyncStreamReader<HelloRequest> requestStream, IServerStreamWriter<HelloReply> responseStream, ServerCallContext context)
		{
			var channel = Channel.CreateUnbounded<HelloReply>();

			var t = Task.Run(async () =>
			{
				await foreach (var helloReply in channel.Reader.ReadAllAsync())
				{
					await responseStream.WriteAsync(helloReply);
				}
			});

			var tasks = new List<Task>();

			try
			{
				await foreach (var request in requestStream.ReadAllAsync())
				{
					tasks.Add(WriteGreetingAsync(request.Name));
				}
			}
			catch (Exception ex)
			{
				Console.WriteLine(ex.ToString());
			}

			await Task.WhenAll(tasks);
			channel.Writer.TryComplete();
			await channel.Reader.Completion;
			await t;

			async Task WriteGreetingAsync(string name)
			{
				await channel.Writer.WriteAsync(new HelloReply()
				{
					Message = "Hello " + name
				});
			}
		}
	}
}
