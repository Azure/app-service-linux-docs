# Node.js on App Service

## Node.js Update Policy

App Service upgrades the underlying Node.js runtime and SDK of your application as part of the regular platform updates. As a result of this update process, your application will be automatically updated to the latest patch version available in the platform for the configured runtime of your app.

### End of Life

Once a version of Node.js has reached it's end of life (EOL) it will no longer be available from Runtime Stack selection dropdown.

Existing applications configured to target a runtime version that has reached EOL should not be affected.

## Support Timeline

|    Version    | Support Status |   End of Support  |   OS Support    |
|---------------| -------------- | ----------------- |---------------- |
|  Node.js 8.x  | End of Life    | December 31 2019  | Windows & Linux |
|  Node.js 9.x  | End of Life    | June 30 2019      | Windows & Linux |
|  Node.js 10.x | End of Life    | April 30 2021     | Windows & Linux |
|  Node.js 12.x | Active LTS     | April 30 2022     | Windows & Linux |
|  Node.js 14.x | Active LTS     | April 30 2023     | Windows & Linux |

[Node.js support timeline](https://nodejs.org/about/releases/)
