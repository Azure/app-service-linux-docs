using Grpc.Core;
using GrpcServerStream;

namespace GrpcServerStream.Services
{
    public class GreeterService : Greeter.GreeterBase
    {
        private readonly ILogger<GreeterService> _logger;
        public GreeterService(ILogger<GreeterService> logger)
        {
            _logger = logger;
        }

        public override async Task SayHello(HelloRequest request, IServerStreamWriter<HelloReply> responseStream, ServerCallContext context)
        {
            foreach (var name in request.Name.Split(","))
            {
                await responseStream.WriteAsync(new HelloReply()
                {
                    Message = "Hello from App Service" + name + "!"
                });

                await Task.Delay(1000);
            }

        }
    }
}