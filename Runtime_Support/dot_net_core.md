# .NET Core on App Service

## .NET Core Update Policy

App Service upgrades the underlying .NET Core runtime and SDK of your application as part of the regular platform updates. As a result of this update process, your application will be automatically updated to the latest patch version available in the platform for the configured minor version of your app.

### End of Life

Once a version of .NET Core has reached it's end of life (EOL) it will no longer be available from Runtime Stack selection dropdown.

Existing applications configured to target a runtime version that has reached EOL should not be affected.

## Support Timeline

|    Version    | Support Status |   End of Support  |   OS Support    |
|---------------| -------------- | ----------------- |---------------- |
| .NET Core 1.0 | End of Life    | June 27 2019      | Windows & Linux |
| .NET Core 1.1 | End of Life    | June 27 2019      | Windows & Linux |
| .NET Core 2.0 | End of Life    | October 1, 2018   | Windows & Linux |
| .NET Core 2.1 | LTS            | August 21, 2021   | Windows & Linux |
| .NET Core 2.2 | Maintenance    | December 23, 2019 | Windows & Linux |
| .NET Core 3.0 | Maintenance    | March 3, 2020     | Windows & Linux |
| .NET Core 3.1 | LTS            | n/a               | Windows & Linux |

[.NET Core Support timeline](https://dotnet.microsoft.com/platform/support/policy/dotnet-core)
