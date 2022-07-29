# Python on App Service

## Python Update Policy

App Service upgrades the underlying Python runtime of your application as part of the regular platform updates. As a result of this regular update process, your application will be automatically updated to the latest patch version of Python available for that platform.

## Support Timeline

|  Version   |  Support Status  | End of Life     |    OS Support   |
|------------| ---------------- |:---------------:|:---------------:|
| Python 3.10| Pending          | November, 2026  | Linux           |
| Python 3.9 | Official Support | October, 2025   | Linux           |
| Python 3.8 | Official Support | October, 2024   | Linux           |
| Python 3.7 | Official Support | June, 2023      | Linux           |
| Python 3.6 | EOL              | December, 2021  | Windows & Linux |
| Python 2.x | EOL              | January, 2020   | Windows & Linux |


[Python Official Support timeline](https://devguide.python.org/#status-of-python-branches)

[Python 2.x Official Support timeline](https://www.python.org/doc/sunset-python-2/)


## End of Life

Once a version of Python has reached it's end of life (EOL) it will no longer be available as a selection in the Azure Portal or Azure CLI.

Existing applications configured to target a runtime version that has reached EOL should continue to work but will be out of support.

No further critical or security fixes will be available.

App Service recommends migrating your application to a supported version.

### Python 3.6 End of Life

If you are currently targeting Windows for Python development you have the option to use a [Windows container](https://azure.github.io/AppService/2021/03/04/How-to-Host-a-Python-application-with-Windows-Containers-on-App-Service.html) going forward, however we recommend you plan for migrating development to target Linux.

After December 23 2021, Linux will be the only OS supported by future versions of Python and continued feature, quality and security updates. 

Once your application is refactored to target Linux, follow the QuickStart documentation for [deploying a Python app using App Service on Linux](https://docs.microsoft.com/azure/app-service/quickstart-python?tabs=bash&pivots=python-framework-flask)

## How to update your app to target a different version of Python

>**NOTE**:
>Changing the stack settings of your app will trigger a re-start of your application.

Update your App Service apps to use a supported version of Python in the Azure portal:
1. In the Azure portal, click the **App Service** blade. Select the app you want to update. 
2. In the Configuration panel, click the **General settings** tab.
3. Under Stack Settings, click the drop-down menu under **Minor version** and select the Python version you want (we recommend choosing the most recent version).
4. Click **Save**.

![Python Minor Version](./media/python.gif)
