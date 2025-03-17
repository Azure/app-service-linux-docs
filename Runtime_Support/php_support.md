# PHP on App Service

## PHP Update Policy

App Service upgrades the underlying PHP runtime of your application as part of the regular platform updates. As a result of this regular update process, your application will be automatically updated to the latest patch version of PHP available in the platform.

### End of Life

Once a version of PHP has reached it's end of life (EOL) it will no longer be available from Runtime Stack selection dropdown.

Existing applications configured to target a runtime version that has reached EOL should not be affected.

## Support Timeline

App Service updates existing stacks after they become available from each community. Please reffer to the official [PHP Official Support timeline](https://www.php.net/supported-versions.php) for the most up to date version support information.

You can find the list of supported versions using the [list-runtimes](https://learn.microsoft.com/cli/azure/webapp?view=azure-cli-latest#az-webapp-list-runtimes) command from the Azure CLI. `az webapp list-runtimes` will list all the versions that are currently supported (not EOL) for a given runtime.

``` bash
# Available runtimes on Linux
az webapp list-runtimes --os-type linux
```

## PHP 8

Official support for PHP 8 will only be available on Linux, as a result of this App Service will only support PHP 8 on Apps Service Linux instances.

## How to update your app to target a different version of PHP

> **NOTE**:
>
> Changing the stack settings of your app will trigger a re-start of your application.

Update your App Service apps to use a supported version of PHP in the Azure portal:

1. In the Azure portal, click the **App Service** blade. Select the app you want to update.
2. In the Configuration panel, click the **General settings** tab.
3. Under Stack Settings, click the drop-down menu under **Minor version** and select the PHP version you want (we recommend choosing the most recent version).
4. Click **Save**.

![PHP Version](./media/php.gif)
