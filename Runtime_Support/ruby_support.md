# Ruby on App Service

## Ruby Update Policy

App Service upgrades the underlying Ruby runtime and SDK of your application as part of the regular platform updates. As a result of this update process, your application will be automatically updated to the latest patch version available in the platform for the configured minor version of your app.

### End of Life

Once a version of Ruby has reached it's end of life (EOL) it will no longer be available from Runtime Stack selection dropdown.

Existing applications configured to target a runtime version that has reached EOL should not be affected.

## Support Timeline

| Version  | Support Status  |   End of Support  |   OS Support    |
|----------| --------------- | ----------------- |---------------- |
| Ruby 2.6 | Supported       | TBA               | Linux |
| Ruby 2.5 | EOL             | March 31, 2021    | Linux |
| Ruby 2.4 | EOL             | April 5th, 2020   | Linux |
| Ruby 2.3 | EOL             | March 31, 2019    | Linux |

[Ruby Official Support timeline](https://www.ruby-lang.org/en/downloads/branches/)
