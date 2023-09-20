using Grpc.Core;
using GrpcServerSK;
using System.Threading.Channels;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.SemanticFunctions;
using Microsoft.SemanticKernel.Orchestration;
using Microsoft.SemanticKernel.Memory;
using System.Threading.Tasks.Dataflow;

namespace GrpcServerSK.Services
{
    public class GreeterService : Greeter.GreeterBase
    {
        private readonly ILogger<GreeterService> _logger;
        public GreeterService(ILogger<GreeterService> logger)
        {
            _logger = logger;
        }

        private readonly KernelBuilder builder = new KernelBuilder();

        public static string? Message2 { get; set; }


        /// <summary>
        /// Unary Call
        /// </summary>
        /// <param name="request"></param>
        /// <param name="context"></param>
        /// <returns></returns>
        public override Task<DataResponse> UnaryCall(DataRequest request, ServerCallContext context)
        {
            Message2 = request.Data;

            return Task.FromResult(new DataResponse
            {
                Message = request.Data

            });
        }

        /// <summary>
        /// Bidirectional stream w/ semantic kernel
        /// </summary>
        /// <param name="requestStream"></param>
        /// <param name="responseStream"></param>
        /// <param name="context"></param>
        /// <returns></returns>
        public override async Task SayHelloBidirectional(IAsyncStreamReader<HelloRequest> requestStream, IServerStreamWriter<HelloReply> responseStream, ServerCallContext conext)
        {

            // creates channel for writing replies
            var channel = Channel.CreateUnbounded<HelloReply>();

            // writes response stream first - for each reply in the channel, it reads the channel and writes the response
            var t = Task.Run(async () =>
            {
                await foreach (var helloReply in channel.Reader.ReadAllAsync())
                {
                    await responseStream.WriteAsync(helloReply);
                }
            });

            builder.WithOpenAITextCompletionService(
                     "text-davinci-003",
                     "<your-openai-key>");

            var kernel = builder.Build();

            // creates tasks list
            var tasks = new List<Task>();

            // reads each request stream, then writes the request name // the names from the client
            try
            {
                await foreach (var request in requestStream.ReadAllAsync())
                {
                    // for each of these I want to summarize the request.name
                    var summarize = kernel.CreateSemanticFunction(request.Name);

                    var result = await summarize.InvokeAsync(Message2);

                    tasks.Add(WriteGreetingAsync(result.ToString()));
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
                    Message = name
                });;
            }
        }

    }
}