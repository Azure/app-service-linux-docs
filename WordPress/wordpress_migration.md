# Migrating WordPress to Linux App Service

There are two ways you can migrate your WordPress site from other hosting providers to Azure Linux App Services. 

## 	1. All-In-One WP Migration Plugin

This is a very popular and trusted plugin used for migrating sites with ease and is also recommended by Azure WordPress team. However there are certain things that needs to be taken care of before you start.

By default, the file upload size for WordPress on Linux App Services is limited to 50MB and it can be increased up to 256MB (Maximum Limit). To change the file upload size limit you need to add the following Application Settings in the App Service and save it. 

|    Application Setting Name    | Default Value | New Value   |
|--------------------------------|---------------|-------------|
|    UPLOAD_MAX_FILESIZE         |      50M      |   256M      |
|    POST_MAX_SIZE               |      128M     |   256M      |    
    
Reference: [Application Settings](./wordpress_application_settings.md)


You can use this plugin for migration if your 'exported' file is less than 256MB. However, if it is more than that, you can either buy the premium version of the plugin which can bypass the file upload limit, or you can manually migrate the site using the steps mentioned in next section.

Once you have resolved the above items, you can follow the below steps to start the migration using this plugin.

1. Install the above plugin on both the sites.
2. Click on Export button on the source site to bundle your database, media files, plugins, and themes into one tidy file and download it. 
3. Click on import option on the destination site, and upload the file downloaded in step(2).
4. Empty the caches in W3TC plugin (or any other caches), and validate the content of the site.
5. It is recommended to revert the file upload size Application Settings back to their default values and restart the App Service.
		
		
	
