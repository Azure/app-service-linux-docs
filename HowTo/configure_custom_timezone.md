# How to configure a custom timezone

UTC is the default timezone configuration for any app.

You can change the timezone by using the app setting `WEBSITE_TIME_ZONE`

The value must be set using the [IANA Timezone Database](https://www.iana.org/time-zones) format.

For quick reference you can reference [this list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List)


## Examples

> **Note:** Adding or modifying App Setting will cause an application re-start.

In this example we will be setting the timezone to `America/Los_Angeles` that corresponds to a UTC offset of -08:00

You can configure this app setting through the [Azure Portal](https://portal.azure.com).

Navigate to your webapp and click on **Configuration>Application Settings> New Application Setting** and providing the name and value:

![Timezone](.\media\timezone_appsettings_ui.png)


You can also configure this app setting through the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/) using the `az webapp config appsettings set` command. You can learn more about this command in the [Azure CLI documentation](https://learn.microsoft.com/cli/azure/webapp/config/appsettings?view=azure-cli-latest)

```bash
az webapp config appsettings set --resource-group <your_resource_group> --name <your_app> --settings WEBSITE_TIME_ZONE=America/Los_Angeles
```

You can confirm the change has been applied to your app's environment through SSH.

App service provides an in browser SSH experience directly in the azure portal. Look for SSH under development tools

You can also SSH to your app using the Azure CLI using the `az webapp ssh` command. Learn more about this command in the [Azure CLI documentation](https://learn.microsoft.com/cli/azure/webapp?view=azure-cli-latest#az-webapp-ssh)

```bash
az webapp ssh --resource-group <your_resource_group> --name <your_app>
```

Once you have established and SSH connection the `date` command will provide the current time in the configured timezone.

![](.\media\timezone_ssh.png)