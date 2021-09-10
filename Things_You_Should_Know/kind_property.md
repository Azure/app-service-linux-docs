# App Service Kind property

Everything in Azure is modeled as a **resource**. You can learn more about resources through [Azure Resource Manager documentation](https://docs.microsoft.com/azure/azure-resource-manager/management/overview)

Every Azure resource has a set of generic properties that are common across all resources. **Kind** is one of this generic azure resource properties. See [Resources - Get](https://docs.microsoft.com/rest/api/resources/resources/get)

There are several different offerings in the azure portal that use the same underlying `Microsoft.Web\Sites` resource. [Learn more about `Microsoft.Web\Sites`](https://docs.microsoft.com/azure/templates/microsoft.web/2019-08-01/sites)

**App Service** uses the value of the **kind property** to specialize the UX of a `Microsoft.Web\Sites` resource in the Azure Portal.

The `kind` property of an app is set during create flow. The portal does this based on the create flow of your choice and/or the configuration you enter. This is also true of the [App Service CLI](https://docs.microsoft.com/cli/azure/appservice?view=azure-cli-latest) and other clients like [Visual Studio Code](https://code.visualstudio.com/).

You will need to manually set the **kind property** if you are creating resources through [ARM templates](https://docs.microsoft.com/azure/azure-resource-manager/templates/), or using the [ARM API directly](https://docs.microsoft.com/rest/api/resources/).

## App Service Resource Kind reference

The following table contains a list of valid values for Kind property:

|Kind                                     | Resource Type                  |
|-----------------------------------------|--------------------------------|
|`app`                                    | Windows Web app                |
|`app,linux`                              | Linux Web app                  |
|`hyperV`                                 | Windows Container Web App      |
|`app,container,windows`                  | Windows Container Web App      |
|`app,linux,kubernetes`                   | Linux Web App on ARC           |
|`functionapp`                            | Function Code App              |
|`functionapp,linux`                      | Linux Consumption Function app |
|`functionapp,linux,container,kubernetes` | Function Container App on ARC  |
|`functionapp,linux,kubernetes`           | Function Code App on ARC       |

There are other kind values that have been valid in the past, however as of this writing this are the only valid `kind` property values in active use.

If the `value` of the kind property is null, empty, or not on this list. The portal treats the resource as Web App.
