# Python on App Service

## Python Update Policy

App Service upgrades the underlying Python runtime of your application as part of the regular platform updates. As a result of this regular update process, your application will be automatically updated to the latest patch version of Python available for that platform.

### Python 2.7 End of Official Support

Once a version of Python has reached it's end of support no new critical or security fixes will be available.

On February 2, 2020 Python 2.7 will not longer be offered as an option in the create process for App Service. Existing apps targeting Python 2.7 will not be affected.

### Python 3.6 End of Official Support

Once a version of Python has reached it's end of support no new critical or security fixes will be available.

On December 23rd, 2021 Python 3.6 will not longer be offered as an option in the create process for App Service. Existing apps targeting Python 3.6 will not be affected.

> If you are currently targeting Windows for Python development, we advise to plan for migrating development to target Linux.  After December 23 2021, Linux will be the only OS supported by future versions of Python and continued feature, quality and security updates.

### Python 3.7 End of Official Support

Once a version of Python has reached it's end of support no new critical or security fixes will be available.

On June 27th, 2023 Python 3.7 will not longer be offered as an option in the create process for App Service. Existing apps targeting Python 3.7 will not be affected.


## Support Timeline

|  Version   |  Support Status  |  End of Official Support |    OS Support   |
|------------| ---------------- |:------------------------:|:---------------:|
| Python 2.x | Official Support |    January 01, 2020      | Windows & Linux |
| Python 3.6 | Official Support |    December 23, 2021      | Windows & Linux |
| Python 3.7 | Official Support |    June 27, 2023      | Linux |

[Python Official Support timeline](https://devguide.python.org/#status-of-python-branches)

[Python 2.x Official Support timeline](https://www.python.org/doc/sunset-python-2/)

## How to update your app to target a different version of Python

>**NOTE**:
>Changing the stack settings of your app will trigger a re-start of your application.

Update your App Service apps to use a supported version of Python in the Azure portal:
1. In the Azure portal, click the **App Service** blade. Select the app you want to update. 
2. In the Configuration panel, click the **General settings** tab.
3. Under Stack Settings, click the drop-down menu under **Minor version** and select the Python version you want (we recommend choosing the most recent version).
4. Click **Save**.

![Python Minor Version](./media/python.gif)