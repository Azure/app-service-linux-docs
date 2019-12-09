# PHP on App Service

## PHP Update Policy

App Service upgrades the underlying PHP runtime of your application as part of the regular platform updates. As a result of this regular update process, your application will be automatically updated to the latest patch version of PHP available in the platform.

### End of Extended Support

Once a version of PHP has reached it's end of extended support your application will be upgraded to the next recommended supported minor version.

For example on February 01, 2020 any application running on `PHP 7.0`  or `PHP 7.1` will be upgraded to `PHP 7.2`

### End of Life for PHP 5.6

Due to the popularity of **PHP 5.6** and the high volume of applications hosted using this version of the PHP runtime. Critical security fixes have been actively backported from the 7.X PHP branch into the version of **PHP 5.6** provided by **Azure App Service**.

Extended support for this version of **PHP 5.6** will end on **February 01, 2021**. At this point any application hosted in App Service targeting this version of the **PHP 5.6** will be out of support and at risk of security vulnerabilities that remain unpatched.

## Support Timeline

| Version |  Support Status  |  End of Official Support | End of Extended Support | OS Support |
|---------| ---------------- |:------------------------:|:-----------------------:| ---------- |
| PHP 5.6 | Extended Support |    January 01, 2019      |    February 01, 2021    | Windows & Linux |
| PHP 7.0 | Extended Support |    December 03, 2018     |    February 01, 2020    | Windows & Linux |
| PHP 7.1 | Extended Support |    December 01, 2019     |    February 01, 2020    | Windows & Linux |
| PHP 7.2 | Official Support |    November 30, 2020     |    February 01, 2021    | Windows & Linux |
| PHP 7.3 | Official Support |    November 28, 2021     |    December 06, 2021    | Windows & Linux |

[PHP Official Support timeline](https://www.php.net/supported-versions.php)
