package com.example.grpc;

import io.grpc.*;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class DemoApplication {

	public static void main(String[] args) throws Exception
	{

		// SPRING BOOT SERVER
		SpringApplication.run(DemoApplication.class, args);

		// gRPC SERVER
		// Create a new server to listen on port 8585
		Server server = ServerBuilder.forPort(8585)
		.addService(new GreetingServiceImpl())
		.build();
	
		server.start();
	
		System.out.println("gRPC server started");

		server.awaitTermination();
	}

	@RequestMapping("/")
	String sayHello() {
		return "gRPC server ready for requests.";
	}
}
