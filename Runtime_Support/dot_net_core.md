# .NET on App Service

## .NET Update Policy

App Service upgrades the underlying .NET runtime and SDK of your application as part of the regular platform updates. As a result of this update, your application will be automatically updated to the latest patch version available in the platform for the configured minor version of your app.

## Support Timeline

|    Version    | Support Status |   End of Support  |   OS Support    |
|---------------| -------------- | ----------------- |---------------- |
| .NET 7        | Early Access   | May 2024          | Windows & Linux |
| .NET 6        | LTS            | November 8, 2024  | Windows & Linux |
| .NET 5        | End of Life    | May 8, 2022       | Windows & Linux |
| .NET Core 3.1 | LTS            | December 3, 2022  | Windows & Linux |
| .NET Core 3.0 | End of Life    | March 3, 2020     | Windows & Linux |
| .NET Core 2.2 | End of Life    | December 23, 2019 | Windows & Linux |
| .NET Core 2.1 | End of Life    | August 21, 2021   | Windows & Linux |
| .NET Core 2.0 | End of Life    | October 1, 2018   | Windows & Linux |
| .NET Core 1.1 | End of Life    | June 27 2019      | Windows & Linux |
| .NET Core 1.0 | End of Life    | June 27 2019      | Windows & Linux |

[.NET Core Support timeline](https://dotnet.microsoft.com/platform/support/policy/dotnet-core)

## Early Access limitations

During the early access period, a runtime will be subject to the **Early Access** limitations listed in the [early access support document](./early_access.md).


### .NET 5 End of Official Support

On May 8th, 2022 .NET 5 will no longer be offered as an option in the create process for App Service. Existing apps targeting .NET 5 will not be affected.

### End of Life

Once a version of .NET has reached it's end of life (EOL) it will no longer be available from Runtime Stack selection dropdown.

Existing applications configured to target a runtime version that has reached EOL should continue to work but will be out of support.

No further critical or security fixes will be available.

App Service recommends migrating your application to supported version.

## How to update your app to target a different version of .NET

>**NOTE**
>
> Changing the stack settings of your app will trigger a re-start of your application.

Update your App Service apps to use a supported version of .NET in the Azure portal:
1. In the Azure portal, click the **App Service** blade. Select the app you want to update. 
2. In the Configuration panel, click the **General settings** tab.
3. Under Stack Settings, click the drop-down menu under **Major version** and select the .NET or  version you want (we recommend choosing the most recent version).
4. Click **Save**.

![Stack Version](./media/dotnet.gif)
