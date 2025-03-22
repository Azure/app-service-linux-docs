# Node.js on App Service

## Node.js Update Policy

App Service upgrades the underlying Node.js runtime and SDK of your application as part of the regular platform updates. As a result of this update process, your application will be automatically updated to the latest patch version available in the platform for the configured runtime of your app.

### End of Life

Once a version of Node.js has reached it's end of life (EOL) it will no longer be available from Runtime Stack selection dropdown.

Existing applications configured to target a runtime version that has reached EOL should not be affected.

## Support Timeline

App Service updates existing stacks after they become available from each community. Please reffer to the official [Node.js support timeline](https://nodejs.org/en/about/releases/) for the most up to date version support information.

You can find the list of supported versions using the [list-runtimes](https://learn.microsoft.com/cli/azure/webapp?view=azure-cli-latest#az-webapp-list-runtimes) command from the Azure CLI. `az webapp list-runtimes` will list all the versions that are currently supported (not EOL) for a given runtime.

``` bash
# Available runtimes on Linux
az webapp list-runtimes --os-type linux

# Available runtimes on Windows
az webapp list-runtimes --os-type windows

```

## How to update your app to target a different version of Node

> **NOTE**:
> Changing the stack settings of your app will trigger a re-start of your application.

### Node on Windows App Service

If you are hosting a node.js app on a Windows webapp, the runtime version of your app is configured through an app setting `WEBSITE_NODE_DEFAULT_VERSION`.

You can change the value of this app setting through the Azure portal, or through Azure CLI:

```azurecli-interactive
az webapp config appsettings set --name <app-name> --resource-group <resource-group-name> --settings WEBSITE_NODE_DEFAULT_VERSION="~16"
```

> **Note:** This example uses the recommended "tilde syntax" to target the latest available version of Node.js 16 runtime on App Service.
> Since the runtime is regularly patched and updated by the platform it's not recommended to target a specific minor version/patch as these are not guaranteed to be available due to potential security risks.

### Node on Linux App Service

If you are hosting a node.js app on a Linux webapp, the runtime version of your app is configured through `linux-fx-version` property.

You can change the target runtime through Azure CLI:

```azurecli-interactive
az webapp config set --resource-group <resource-group-name> --name <app-name> --linux-fx-version "NODE|14-lts"
```

You can also change the runtime throgh the Azure portal:

1. In the Azure portal, click the **App Service** blade. Select the app you want to update.
2. In the Configuration panel, click the **General settings** tab.
3. Under Stack Settings, click the drop-down menu under **Major version** and select the Node version you want (we recommend choosing the most recent version).
4. Click **Save**.

![Node Version](./media/node.gif)
