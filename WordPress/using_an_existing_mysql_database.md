# Using an existing MySQL database  

1. It is recommended to ensure that both App Service(web server) and database server are running in the same region to avoid performance issues.
2. It is recommended to use [Azure MySQL Flexible Server](https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.DBforMySQL%2FflexibleServers) as database.
3. It is recommended to keep the database in the same VNET as your App Service. Follow the steps described [here](https://docs.microsoft.com/en-us/azure/mysql/flexible-server/how-to-manage-virtual-network-portal).
4. The MySQL database version should be compatible with the new WordPress version running on Linux App Service.
5. Backup your WordPress site and database. Please see [WordPress backups](https://wordpress.org/support/article/wordpress-backups/) and [Backing up your database](https://wordpress.org/support/article/backing-up-your-database/) for more details.
6. Launch the Azure Portal and navigate to your **App Service -> Configuration** blade. Update the database name in the **Application Settings** of App Service and save it. This will restart your App and the new changes will get reflected.

    |    Application Setting Name    |
    |--------------------------------|
    |    DATABASE_NAME               |
    |    DATABASE_HOST               |
    |    DATABASE_USERNAME           |
    |    DATABASE_PASSWORD           |
    
    Reference: [WordPress Application Settings](./wordpress_application_settings.md)

