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




50M

256M



128M

256M





### .NET 5 End of Official Support

Once a version of .NET has reached it's end of support no new critical or security fixes will be available.

On May 8th, 2022 .NET 5 will no longer be offered as an option in the create process for App Service. Existing apps targeting .NET 5 will not be affected.  We recommend migrating your application to .NET 6 when available in November.  See our guidance [below](#how-to-update-your-app-to-target-a-different-version-of-dotnet) to target a new version.

### End of Life

Once a version of .NET Core has reached it's end of life (EOL) it will no longer be available from Runtime Stack selection dropdown.

Existing applications configured to target a runtime version that has reached EOL should not be affected.

## .NET 5 Early Access limitations

During the early access period, .NET 5 apps will be subject to the **Early Access** limitations listed in the [early access support document](./early_access.md).

[Application Insights](https://azure.microsoft.com/services/monitor) is currently not supported for .NET 5 apps, we are working with the Application Insights team to resolve this.

Visual Studio and Visual Studio for Mac will not support creating new .NET 5 Apps on App Service through the IDE at launch. As a workaround .NET 5 Apps can be created from the Azure Portal or Azure CLI.
Publishing content to a .NET 5 app works as expected. There is a schedule update that will remove this limitation.

## Support Timeline

|    Version    | Support Status |   End of Support  |   OS Support    |
|---------------| -------------- | ----------------- |---------------- |
| .NET 6        | LTS            | November 8, 2024    | Windows & Linux |
| .NET 5        | Current        | May 8, 2022         | Windows & Linux |
| .NET Core 3.1 | LTS            | December 3, 2022  | Windows & Linux |
| .NET Core 3.0 | End of Life    | March 3, 2020     | Windows & Linux |
| .NET Core 2.2 | End of Life    | December 23, 2019 | Windows & Linux |
| .NET Core 2.1 | End of Life    | August 21, 2021   | Windows & Linux |
| .NET Core 2.0 | End of Life    | October 1, 2018   | Windows & Linux |
| .NET Core 1.1 | End of Life    | June 27 2019      | Windows & Linux |
| .NET Core 1.0 | End of Life    | June 27 2019      | Windows & Linux |

[.NET Core Support timeline](https://dotnet.microsoft.com/platform/support/policy/dotnet-core)


## How to update your app to target a different version of .NET or .NET Core

>**NOTE**:
>Changing the stack settings of your app will trigger a re-start of your application.

Update your App Service apps to use a supported version of .NET or .NET Core in the Azure portal:
1. In the Azure portal, click the **App Service** blade. Select the app you want to update. 
2. In the Configuration panel, click the **General settings** tab.
3. Under Stack Settings, click the drop-down menu under **Major version** and select the .NET or .NET Core version you want (we recommend choosing the most recent version).
4. Click **Save**.

![Node Version](./media/dotnet.gif)
