# Use KeyVault Reference in Linux App Service

## Store Credentials as Application Settings
Many Linux web app connects to a database server such as Azure MySQL etc. To avoid committing the password to source code, we recommend customers to store the credentials as “application settings”. At web app startup time, the application settings get passed as -e(s) to the Docker container which hosts the web app. At runtime, the web app can programmably retrieve the application settings as Linux environment variables. Here is some sample PHP code which retrieves the MySQL connection information and constructs a connection string:
```
// MySQL database configuration
$servername = getenv('DATABASE_HOST');
$username = getenv('DATABASE_USERNAME');
$password = getenv('DATABASE_PASSWORD');
$dbname = getenv('DATABASE_NAME');

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
die("Connection failed: " . $conn->connect_error);
} 
```

## KeyVault Reference
The issue with this approach is that application settings are visible on Azure portal under on the “Application settings” section, even though we encrypt the key/value pairs during transmission and when stored in our internal database. We made improvements on UX to mask out the value of application settings but customer can still see the values when unmask it.

With Managed Identities feature enabled for Linux App Service, customer can now store the credentials in a KeyVault and make reference to the KeyVault in application settings instead of using plain text. Here is how to configure it:
1. Create a key vault by following the [Key Vault quickstart](https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli).
2. Create a [system-assigned managed identity](https://docs.microsoft.com/en-us/azure/app-service/overview-managed-identity) for your application.
3. Create an [access policy in Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/key-vault-secure-your-key-vault#key-vault-access-policies) for the application identity you created earlier. Enable the "Get" secret permission on this policy. Do not configure the "authorized application" or appliationId settings, as this is not compatible with a managed identity.      
4. Construct the KeyVault reference following the [instructions](https://docs.microsoft.com/en-us/azure/app-service/app-service-key-vault-references#reference-syntax). 
5. Go to the web app on Azure portal, find the application setting that you would like to repalce with KeyVault refrence. Once you save the change, the web app will restart. Please double check if the site is functioning correctly.

Debug tips: to debug issues with KeyVault refreence in Linxu Web App, you can find the “decoded” application setting values on Kudu site under: https://your_site_name.scm.azurewebsites.net/api/settings  

