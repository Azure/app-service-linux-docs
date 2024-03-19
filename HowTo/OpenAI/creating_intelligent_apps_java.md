# Creating Intelligent Apps on App Service (Java)

You can use Azure App Service to create applications using Azure OpenAI and OpenAI.  In the following tutorial we will be adding an Azure OpenAI service to a Java 17 Spring Boot application using the Azure SDK.

### Prerequisites

- An�[Azure OpenAI resource](https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart?pivots=programming-language-csharp&tabs=command-line%2Cpython#set-up)�or an�[OpenAI account](https://platform.openai.com/overview).
- A Java spring boot application. Create the application using this [quickstart](https://learn.microsoft.com/en-us/azure/app-service/quickstart-java?tabs=springboot&pivots=java-maven-javase).

### Setup web app

For this Spring Boot application, we�ll be building off the [quickstart](https://learn.microsoft.com/en-us/azure/app-service/quickstart-java?tabs=springboot&pivots=java-maven-javase) app and adding an additional feature to make a request to an Azure OpenAI or OpenAI service.  Add the following code to your application:

```bash
  @RequestMapping("/")
	String sayHello() {

	   String serverResponse = "";
   
	   return serverResponse;
  }
```

**API Keys and Endpoints**

First, you will need to grab the keys and endpoint values from Azure OpenAI or OpenAI and add them as secrets for use in your application. Retrieve and save the values for later use to build the client.

For Azure OpenAI, see�[this documentation](https://learn.microsoft.com/azure/ai-services/openai/quickstart?pivots=programming-language-csharp&tabs=command-line%2Cpython#retrieve-key-and-endpoint)�to retrieve the key and endpoint values. For our application, you will need the following values:

1. endpoint
2. apiKey
3. deploymentName

For OpenAI, see this�[documentation](https://platform.openai.com/docs/api-reference)�to retrieve the API keys. For our application, you will need the following values:

1. apiKey
2. modelName

Since we�ll be deploying to App Service we can secure these secrets in�**Azure Key Vault**�for protection. Follow the�[Quickstart](https://learn.microsoft.com/azure/key-vault/secrets/quick-create-cli#create-a-key-vault)�to setup your Key Vault and add the secrets you saved from earlier.

Next, we can use Key Vault references as app settings in our App Service resource to reference in our application. Follow the instructions in the�[documentation](https://learn.microsoft.com/azure/app-service/app-service-key-vault-references?source=recommendations&tabs=azure-cli)�to grant your app access to your Key Vault and to setup Key Vault references.

Then, go to the portal Environment Variables blade in your resource and add the following app settings:

For Azure OpenAI, use the following:

1. API_KEY = @Microsoft.KeyVault(SecretUri=[https://myvault.vault.azure.net/secrets/mysecret/](https://myvault.vault.azure.net/secrets/mysecret/))
2. ENDPOINT = @Microsoft.KeyVault(SecretUri=[https://myvault.vault.azure.net/secrets/mysecret/](https://myvault.vault.azure.net/secrets/mysecret/))
3. DEPOYMENT_NAME = @Microsoft.KeyVault(SecretUri=[https://myvault.vault.azure.net/secrets/mysecret/](https://myvault.vault.azure.net/secrets/mysecret/))

For OpenAI, use the following:

1. OPENAI_API_KEY = @Microsoft.KeyVault(SecretUri=[https://myvault.vault.azure.net/secrets/mysecret/](https://myvault.vault.azure.net/secrets/mysecret/))
2. OPENAI_MODEL_NAME = @Microsoft.KeyVault(SecretUri=[https://myvault.vault.azure.net/secrets/mysecret/](https://myvault.vault.azure.net/secrets/mysecret/))

Once your app settings are saved, you can access the app settings in your code by referencing them in your application.  Add the following code in the *[Application.java](http://Application.java)* file:

```bash
  @RequestMapping("/")
	String sayHello() {

      // Azure OpenAI
      Map<String, String> envVariables = System.getenv();
      String apiKey = envVariables.get("API_KEY");
      String endpoint = envVariables.get("ENDPOINT");
      String depoymentName = envVariables.get("DEPLOYMENT_NAME");

      // OpenAI
      Map<String, String> envVariables = System.getenv();
      String apiKey = envVariables.get("OPENAI_API_KEY");
      String modelName = envVariables.get("OPENAI_MODEL_NAME");
  }  

```

### Add the package

Before you can create the client, you first need to add the Azure SDK dependency.  Add the following Azure OpenAI package to the *pom.xl* file and run the **mvn package** command to build the package.

```python
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-ai-openai</artifactId>
    <version>1.0.0-beta.6</version>
</dependency>
```

Once the package is created we can start working on the client that will make our calls.

### Create OpenAI client

Once the package and environment variables are setup, we can create the client that will enable chat completion calls.

Add the following code to create the OpenAI client: 

For Azure OpenAI:

```java
OpenAIClient client = new OpenAIClientBuilder()
    .credential(new AzureKeyCredential(apiKey))
    .endpoint(endpoint)
    .buildClient();
```

For OpenAI:

```java
OpenAIClient client = new OpenAIClientBuilder()
    .credential(new KeyCredential(apiKey))
    .buildClient();
```

Once added, you will see the following imports will be added to the [Application.java](http://Application.java) file:

```java
import com.azure.ai.openai.OpenAIClient;
import com.azure.ai.openai.OpenAIClientBuilder;
import com.azure.core.credential.AzureKeyCredential;
```

### Setup prompt and call to OpenAI

Now that our OpenAI service is created we can use the chat completions method to send our request message to OpenAI and return a response.  Here is where we will add our chat message prompt to the code to be passed to the chat completions method.  Use the following code to setup the chat completions method:

```java
List<ChatRequestMessage> chatMessages = new ArrayList<>();
        chatMessages.add(new ChatRequestUserMessage("What is Azure App Service in one line tldr?"));

// Azure OpenAI
ChatCompletions chatCompletions = client.getChatCompletions(deploymentName,
    new ChatCompletionsOptions(chatMessages));

// OpenAI
ChatCompletions chatCompletions = client.getChatCompletions(modelName,
    new ChatCompletionsOptions(chatMessages));
```

Here is the example in it�s completed from.  In this example, use the Azure OpenAI chat completion service OR the OpenAI chat completion service, not both.

```java

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.azure.ai.openai.OpenAIClient;
import com.azure.ai.openai.OpenAIClientBuilder;
import com.azure.ai.openai.models.ChatChoice;
import com.azure.ai.openai.models.ChatCompletions;
import com.azure.ai.openai.models.ChatCompletionsOptions;
import com.azure.ai.openai.models.ChatRequestMessage;
import com.azure.ai.openai.models.ChatRequestUserMessage;
import com.azure.ai.openai.models.ChatResponseMessage;
import com.azure.core.credential.AzureKeyCredential;

@SpringBootApplication
@RestController
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }

  @RequestMapping("/")
	String sayHello() {

        String serverResponse = "";

        // Azure OpenAI
        Map<String, String> envVariables = System.getenv();
        String apiKey = envVariables.get("API_KEY");
        String endpoint = envVariables.get("ENDPOINT");
        String deploymentName = envVariables.get("DEPLOYMENT_NAME");

        // OpenAI
        // Map<String, String> envVariables = System.getenv();
        // String apiKey = envVariables.get("OPENAI_API_KEY");
        // String modelName = envVariables.get("OPENAI_MODEL_NAME");

        // Azure OpenAI client
        OpenAIClient client = new OpenAIClientBuilder()
        .credential(new AzureKeyCredential(apiKey))
        .endpoint(endpoint)
        .buildClient();

        // OpenAI client
        // OpenAIClient client = new OpenAIClientBuilder()
        // .credential(new KeyCredential(apiKey))
        // .buildClient();

        // Chat Completion
        List<ChatRequestMessage> chatMessages = new ArrayList<>();
        chatMessages.add(new ChatRequestUserMessage("What's is Azure App Service in one line tldr?"));

        // Azure OpenAI
        ChatCompletions chatCompletions = client.getChatCompletions(deploymentName,
            new ChatCompletionsOptions(chatMessages));

        // OpenAI
        // ChatCompletions chatCompletions = client.getChatCompletions(modelName,
        //     new ChatCompletionsOptions(chatMessages));

        System.out.printf("Model ID=%s is created at %s.%n", chatCompletions.getId(), chatCompletions.getCreatedAt());
        for (ChatChoice choice : chatCompletions.getChoices()) {
            ChatResponseMessage message = choice.getMessage();
            System.out.printf("Index: %d, Chat Role: %s.%n", choice.getIndex(), message.getRole());
            System.out.println("Message:");
            System.out.println(message.getContent());

            serverResponse = message.getContent();
        }

		return serverResponse;
	}

}
```

### Deploy to App Service

If you completed the steps above you can deploy to App Service as you normally would. If you run into any issues remember that you need to have done the following: grant your app access to your Key Vault, add the app settings with key vault references as your values. App Service will resolve the app settings in your application that match what you�ve added in the portal.

Once deployed, you can visit your site URL and you will be greeted with the text that contains the response from your chat message prompt.  

[blazor](https://github.com/Azure/app-service-linux-docs/blob/master/HowTo/images/blazor_openai.png?raw=true)

**Authentication**

Although optional, it is highly recommended that you also add authentication to your web app when using an Azure OpenAI or OpenAI service. This can add a level of security with no additional code. Learn how to enable authentication for your web app�[here](https://learn.microsoft.com/azure/app-service/scenario-secure-app-authentication-app-service).

Once deployed, browse to the web app and navigate to the Open AI tab. Enter a query to the service and you should see a populated response from the server. The tutorial is now complete and you now know how to use OpenAI services to create intelligent applications.