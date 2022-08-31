# WordPress Migration to Linux App Service

This document describes two different approaches to migrating your WordPress sites from any hosting provider to Azure Linux App Services. These migration approaches will let you continue with the existing WordPress site as it is. It is recommended to transition the traffic to the new site after proper validation.

**Note:** Migrate the content to a test instance first, validate all E2E scenarios of your website, and if everything works as expected, swap this instance to the production slot.
 

## 	1. All-In-One WP Migration Plugin

This is a very popular and trusted plugin used for migrating sites with ease and is also recommended by the Azure WordPress team. However, there are certain things that need to be taken care of before starting on the WordPress migration.


This approach is recommended for smaller sites where the content size is less than 256MB. If it is more, you can either **purchase the premium version** of the plugin, which allows you to bypass the file upload limit, or you can **manually migrate** the site using the steps outlined in the next section.


By default, the file upload size for WordPress on Linux App Services is limited to 50MB, and it can be increased up to 256MB (Maximum Limit). To change the file upload size limit, you need to add the following Application Settings in the App Service and save it.


|    Application Setting Name    | Default Value | New Value   |
|--------------------------------|---------------|-------------|
|    UPLOAD_MAX_FILESIZE         |      50M      |   256M      |
|    POST_MAX_SIZE               |      128M     |   256M      |    
    

If you choose to migrate the site using this plugin, install All-In-One Migration plugin on both source and target sites.

### Export the data at source site: 
1.	Launch WordPress Admin page
2.	Open All-In-One WP Migration plugin
3.	Click on 'Export' option and specify the export type as file
4.	This bundles the contents of database, media files, plugins, and themes into a single file, which can then be downloaded.

### Import the data at destination site: 
1.  Launch WordPress Admin page
2.	Open All-In-One WP Migration plugin
3.	Click on import option on the destination site, and upload the file downloaded in previous section
4.	Empty the caches in W3TC plugin (or any other caches) and validate the content of the site.
    a. Click on the **Performance** option given in the left sidebar of the admin panel to open the W3TC plugin.
    b. Then click on the **Dashboard** option shown below it.
    c. On the dashboard, you will see a button with the label **Empty All Caches**.


### Recommended Plugins:
Usually it is not required, but after the site migration, it is better to validate that you have the default recommended plugins activated and configured properly as before. If you are strictly bound to not using them, then you can remove the plugins.

-The W3TC plugin should be activated and configured properly to use the local Redis cache server and Azure CDN/Blob Storage (if it was configured to use them originally).

-WP Smush plugin is activated and configured properly for image optimization. Please see [Image Compression] (./wordpress_image_compression.md) for more information on configuration.


### Recommended WordPress Settings:
The following WordPress settings are recommended. However, when the users migrate their custom sites, is it up to them to decide whether to use these settings or not.

1. Open the WordPress Admin dashboard.
2. Set the permalink structure to 'day and name', which performs better compared to the plain permalink structure (which uses the format?p=123).
3. Under the comment settings, enable the option to break comments into pages.
4. Show excerpts instead of the full post in the feed.
