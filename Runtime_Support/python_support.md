# Python on App Service

## Python Update Policy

App Service upgrades the underlying Python runtime of your application as part of the regular platform updates. As a result of this regular update process, your application will be automatically updated to the latest patch version of Python available for that platform.

### End of Life

Once a version of .NET Core has reached it's end of life (EOL) it will no longer be available from Runtime Stack selection dropdown.

Existing applications configured to target a runtime version that has reached EOL should not be affected.

### Python on Windows End of Official Support

Python on Windows App Service has been unsupported since December 23, 2021 with the end of support for Python 3.6. After that date, Linux has been the only supported OS for Python versions going forward and Python apps using Windows no longer receive security patches or customer service. If you have Python on Windows applications, we strongly urge you to update your apps to a supported version of Python on Linux or migrate your application to use a Windows container.

See the available options to migrate your Python apps below:

- Follow the quickstart documentation to deploy a [Python app using Linux App Service](https://docs.microsoft.com/azure/app-service/quickstart-python?tabs=bash&pivots=python-framework-flask)
- Follow the instructions for hosting a Python app using a [Windows container](https://azure.github.io/AppService/2021/03/04/How-to-Host-a-Python-application-with-Windows-Containers-on-App-Service.html)

## Support Timeline

App Service updates existing stacks after they become available from each community. Please reffer to the official [Python support timeline](https://devguide.python.org/#status-of-python-branches) for the most up to date version support information.

You can find the list of supported versions using the [list-runtimes](https://learn.microsoft.com/cli/azure/webapp?view=azure-cli-latest#az-webapp-list-runtimes) command from the Azure CLI. `az webapp list-runtimes` will list all the versions that are currently supported (not EOL) for a given runtime.

``` bash
# Available runtimes on Linux
az webapp list-runtimes --os-type linux
```

## How to update your app to target a different version of Python

> **NOTE**:
> Changing the stack settings of your app will trigger a re-start of your application.

Update your App Service apps to use a supported version of Python in the Azure portal:

1. In the Azure portal, click the **App Service** blade. Select the app you want to update.
2. In the Configuration panel, click the **General settings** tab.
3. Under Stack Settings, click the drop-down menu under **Minor version** and select the Python version you want (we recommend choosing the most recent version).
4. Click **Save**.

![Python Version](./media/python.gif)
