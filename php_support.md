# PHP on App Service

## PHP Update Policy

App Service upgrades the underlying PHP runtime of your application as part of the regular platform updates. As a result of this regular update process, your application will be automatically updated to the latest patch version of PHP available in the platform.

### End of Extended Support

Once a version of PHP has reached it's end of extended support your application will be upgraded to the next recommended supported minor version.

For example on February 01, 2020 any application running on `PHP 7.0`  or `PHP 7.1` will be upgraded to `PHP 7.3`

## Support Timeline

| Version |  Support Status  |  End of Official Support | End of Extended Support | OS Support |
|---------| ---------------- |:------------------------:|:-----------------------:| ---------- |
| PHP 7.0 | Extended Support |    December 03, 2018     |    February 01, 2020    | Windows & Linux |
| PHP 7.1 | Official Support |    December 03, 2019     |    February 01, 2020    | Windows & Linux |
| PHP 7.2 | Official Support |    October 30, 2020      |    February 01, 2021    | Windows & Linux |

[PHP Official Support timeline](https://www.php.net/supported-versions.php)
