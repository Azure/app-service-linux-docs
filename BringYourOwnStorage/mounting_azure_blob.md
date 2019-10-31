# Updates for Bring your Own Storage preview feature in Azure App Service

Azure App Service apps running on Linux support mapping an Azure Storage container (backed by [Azure Blob](https://docs.microsoft.com/azure/storage/blobs/) or [Azure Files](https://docs.microsoft.com/azure/storage/files/)) to a path accessible by your application ( [learn more](https://docs.microsoft.com/azure/app-service/containers/how-to-serve-content-from-azure-storage) ).

Currently, both options support **read /write** scenarios. Due to limitations in the [drivers used to provide the Azure Blob mounting functionality](https://github.com/Azure/azure-storage-fuse#if-your-workload-is-not-read-only), **mappings backed by Azure Blob will become read-only on February 2nd 2020**. Azure Files backed configurations **will not** be affected by this change.

If your app needs to continue to support read/write scenarios with mounted storage, we recommend using Azure Files.

If you want to opt-in the read only behavior for read only Azure Blob mounts, you can add an app setting:

``` bash
WEBSITE_DISABLE_BYOS_BLOB_READ_WRITE = <mount-name-01>, <mount-name-02>,..., <mount-name-N>
```

The value for this app setting should be a coma delimited list of mount names you want to make read only.

## Example

![Path Mappings][Path_Mappings]

If you have 2 containers mounted to your app and you only want to make the **media** container read-only. Add an app setting with the following Key / Value:

``` bash
WEBSITE_DISABLE_BYOS_BLOB_READ_WRITE = media
```

If you want to make both mounts read only:

``` bash
WEBSITE_DISABLE_BYOS_BLOB_READ_WRITE = media, logs
```

## Learn more

- [App Settings](https://docs.microsoft.com/azure/app-service/configure-common#configure-app-settings)
- [Mounted Storage](https://docs.microsoft.com/azure/app-service/containers/how-to-serve-content-from-azure-storage)
- [Azure App Service](https://docs.microsoft.com/azure/app-service/)

[Path_Mappings]: ./media/mounting_azure_blob.png
