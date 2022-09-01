
# WordPress Application Settings

It is very important to note that there are two types of Application Settings.
1. **Persistent** Application Settings which are impactful throughout the entire lifetime of your WordPress application. Any changes to these settings will update the same in your WordPress application.
	
2. **Non-Persistent** Application Settings which are used as a 'one-time' reference during the installation process. Any subsequent changes to these App Settings after the installation is complete will not update the same in WordPress application. 


## Persistent Application Settings


| Application Setting  |	Scope	 | Default Value |	Max	Value  | Description                      |
|----------------------|-------------|---------------|-------------|----------------------------------|
|WEBSITES_CONTAINER_START_TIME_LIMIT|	Web App|	900|	-|	The amount of time the platform will wait (for the site to come up) before it restarts your container. WP installation takes around 5-10 mins after the AppService is deployed. By default, timeout limit for Linux AppService is 240 seconds. So, overriding this value to 900 seconds for WordPress deployments to avoid container restarts during the setup process. This is a required setting, and it is recommended to not change this value.|
|WEBSITES_ENABLE_APP_SERVICE_STORAGE|	Web App|	TRUE|	-|	When set to TRUE, file contents are preserved during restarts.|
|WP_MEMORY_LIMIT|	WordPress|	128M|	512M|	Frontend or general wordpress PHP memory limit (per script). Can't be more than PHP_MEMORY_LIMIT|
|WP_MAX_MEMORY_LIMIT|	WordPress|	256M|	512M|	Admin dashboard PHP memory limit (per script). Generally Admin dashboard/ backend scripts takes lot of memory compared to frontend scripts. Can't be more than PHP_MEMORY_LIMIT.|
|PHP_MEMORY_LIMIT|	PHP|	512M|	512M|	Memory limits for general PHP script. It can only be decreased.|
|FILE_UPLOADS|	PHP|	On|	-|	Can be either On or Off. Note that values are case sensitive. Enables or disables file uploads.|
|UPLOAD_MAX_FILESIZE|	PHP|	50M|	256M| Max file upload size limit. Can be increased up to 256M.	This value is limited on the upper side by the value of POST_MAX_SIZE variable.|
|POST_MAX_SIZE|	PHP|	128M|	256M|	Can be increased up to 256M. Generally should be more than UPLOAD_MAX_FILESIZE.|
|MAX_EXECUTION_TIME|	PHP|	120|	120|	Can only be decreased. Please break down the scripts if it is taking more than 120 seconds. Added to avoid bad scripts from slowing the system.|
|MAX_INPUT_TIME|	PHP|	120|	120|	Max time limit for parsing the input requests. Can only be decreased.|
|MAX_INPUT_VARS|	PHP|	10000|	10000|	-|
|DATABASE_HOST|	Database|	-|	-|	Database host used to connect to WordPress.|
|DATABASE_NAME|	Database|	-|	-|	Database name used to connect to WordPress.|
|DATABASE_USERNAME|	Database|	-|	-|	Database username used to connect to WordPress.|
|DATABASE_PASSWORD|	Database|	-|	-|	Database password used to connect to WordPress.|




## Non-Persistent Application Settings

Note that these are used only once during the installation process and any subsequent changes to these application settings after installation will not impact the WordPress application.


| Application Setting  |	Scope	       | Default Value |	Max	Value  | Description                      |
|----------------------|-------------------|---------------|-------------|----------------------------------|
|SETUP_PHPMYADMIN|	PhpMyAdmin|	TRUE|	-|	Setups PhpMyAdmin dashboard and can be accessed from /phpmyadmin on your site. Only used once during the installation process. It is recommended to not change this once the WordPress installation is complete as it might change the routing rules.|
|CDN_ENABLED|	Azure CDN|	-|	-|	Enables and configures CDN during installation time if the flag is set to true.|
|CDN_ENDPOINT|	Azure CDN|	-|	-|	The CDN endpoint is configured in the WordPress during installation time. CDN takes around 15 minutes to come up and get configured. CDN_ENABLED flag has to be set to true for this to be configured.|
|BLOB_STORAGE_ENABLED|	Azure Blob Storage|	-|	-|	Enables and configures blob during installation time if the flag is set to true.|
|STORAGE_ACCOUNT_NAME|	Azure Blob Storage|	-|	-|	
|BLOB_CONTAINER_NAME|	Azure Blob Storage|	-|	-|	
|STORAGE_ACCOUNT_KEY|	Azure Blob Storage|	-|	-|	
|WORDPRESS_ADMIN_EMAIL|	WordPress Setup|	-|	-|	
|WORDPRESS_ADMIN_USER|	WordPress Setup|	-|	-|	
|WORDPRESS_ADMIN_PASSWORD|	WordPress Setup|	-|	-|	
|WORDPRESS_TITLE|	WordPress Setup|	-|	-|	
|WORDPRESS_LOCALE_CODE|	WordPress Setup|	en_US|	-|	WordPress localization code for site language.|


<br>

## Configuring Application Settings
Go to the Azure Portal and navigate to your **App Service -> Configuration** blade. Update the required **Application Settings** of App Service and save it. This will restart your App and the new changes will get reflected. 
![Application Settings](./media/wordpress_database_application_settings.png)
