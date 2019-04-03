## Mount an Azure Files or Azure Blob Account to Multi-container Web App 

To mount a storage account to Multi-container web app, first you need to use Azure Portal or CLI to configure a storage account. On Azure Portal, you can add the Storage Account from the "Mount storage (Preview)" section from "Application settings". 

For CLI, please use the following command to configure the storage account.
```
$ az webapp config storage-account add -g RESOURCE_GROUP -n APP_NAME \
  --custom-id CustomId [Unique identifier for this storage mapping] \
  --storage-type [Azure storage type: AzureFiles or AzureBlob]   \
  --account-name [Azure storage account name]   \
  --share-name   [Azure storage share/file name]   \
  --access-key   [storage access key]   \
  --mount-path   [/path/to/mount within the container]
```
Sample command:
```
$ az webapp config storage-account add -g <resource_group> -n <site_name> --custom-id <custom_id> --storage-type AzureBlob --account-name <storage_account_name> --share-name <blob_conatiner_name> --access-key <your_access_key> --mount-path <path_in_conatiner>

Output:
{
    "<custom_id>": {
	"accessKey": "<your_access_key> ",
	"accountName": "<storage_account_name>",
	"mountPath": "<path_in_conatiner>",
	"shareName": "<blob_conatiner_name>",
	"state": "Ok",
	"type": "AzureBlob"
   }
}
```
Once the web app has mounted the Blob storage account to <path_in_conatiner> (e.g. /data/path1), your web app can access to this storage account during runtime. 

If you want to use the mounted storage account in a Multi-container web app,  you need to specify the custom-id of your storage account in the volumes block of the Docker-Compose yaml file, for example:
```  
  version: '3'
  services:
    web:
      image: "docker-registry/image:tag"
      ports:
        – "80:80"
      volumes:
        – <custom-id>:<path_in_conatiner>
    redis:
      image: "redis"
```
Now your "web" conatiner can acesss the mounted storage at <path_in_conatiner>.

