# Configuring Azure Blob Storage with WordPress
**Azure Blob Storage** reduces the load on the web server by serving media files of WordPress (i.e files in wp-content/uploads folder) through a Blob Container. Media files such as images & video are delivered by secure read-only https hyperlinks. 

For Linux WordPress offering, a new Azure storage account with blob container is created using the standard performance tier. Blob Storage details are then configured into WordPress using W3 Total Cache plugin and the settings can be seen in the CDN tab of the plugin's settings. 

Media files are spontaneously pushed to Blob container by **W3 Total Cache** plugin when uploaded, without any manual intervention. Images can be accessed using hyperlinks that point to Blob Storage. It is not recommended to change plugin settings to serve non-Media files such as .js or .css since these files are not spontaneously uploaded to Blob container.

Blob Storage reduces the dependency on App Service storage which is usually limited in size. You can also free up disk space on App Service by deleting the Media files in wp-content/uploads folder, if they are already stored in Blob Storage. It is however recommended to ensure Blob Storage has all files present in App Service before deleting.

Blob Storage has retention policy enabled which allows to restore deleted blobs/containers up to 7 days after being deleted. By default, Blob Storage supports only HTTPS protocol. In case support for HTTP is required, this option can be changed in Storage Account settings in the Azure Portal at **Storage Account -> Settings -> Configuration**. 

The following Application Settings are passed on to the Web App during the deployment in order to configure Azure Blob Storage usage in WordPress. Please note that these settings are only used as a 'one-time' reference during the deployment time and any subsequent change to these settings later on will not update the same in WordPress.

|Application Settings|
|--------------------|
|BLOB_STORAGE_ENABLED|
|STORAGE_ACCOUNT_NAME|
|STORAGE_ACCOUNT_KEY |
|BLOB_CONTAINER_NAME |


### Miscellaneous Information:
- Blob Storage is configured with WordPress using **W3 Total Cache** plugin and its settings can be seen in the CDN tab of the plugin's settings. In this tab, it is not recommended to change settings to host wp-includes/ files, theme files or other non-Media files that are not in wp-content/uploads folder. Enabling these settings will change these files' URL that point to Blob Storage and this can lead to issues if the files are not present in Blob Storage (which usually would be the case since non-Media files are not spontaneously uploaded to Blob Storage).

- Storage Account settings are defined in W3 Total Cache CDN tab. Storage Account Key can be visible to Administrators.  Azure Blog Storage container setting is set to ‘public, read-only’  blob access.

- In case Blob Storage needs to be disabled, then in addition to disabling CDN in W3Total Cache settings, files from Blob Container need to be moved to wp-content/uploads folder in AppService if not already present.

- If Custom Domain or CDN is enabled for Blob Storage, then the domain name needs to be updated in **'Configuration -> Replace site's hostname with'** setting in W3 Total Cache CDN settings.

**Note:** Azure Blob Storage currently doesn't support SSL with custom domain. Click here for more information on custom domain mapping to Azure Blob Storage.


**Reference Links:**<br>
[Introduction to Azure Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blobs-introduction)<br>
[Storage account overview - Azure Storage | Microsoft Docs](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-overview#performance-tiers)<br>
[W3 Total Cache – WordPress plugin | WordPress.org](https://wordpress.org/plugins/w3-total-cache/) <br>
