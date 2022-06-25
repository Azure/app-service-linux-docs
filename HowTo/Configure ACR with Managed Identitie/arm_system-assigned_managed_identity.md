# How to use system-assigned Managed Identities with ARM templates and Azure Container Registry

> **NOTE**:
>
> - These instructions only apply to Linux based containers configurations.
> - The Azure Container registry must be internet accessible.
>   - Pulling container images through a Private Link / Private endpoint connection is currently **not supported**.

App Service can use **system-assigned** [managed identities](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview) to authenticate against **Azure Container Registry (ACR)** and perform `docker pull` operation.

Using **managed identities** is a best practice because they allow for the principle of _least privileged_ access to be followed compared to using the **admin** accounts.

## Prerequisites

This guide uses the [Azure ARM Templates](https://docs.microsoft.com/azure/azure-resource-manager/templates/) to configure your resources. You should already have an Azure Container Registry (ACR) that your want to use. Learn more about [ACR](https://docs.microsoft.com/azure/container-registry/).

If you are starting with an empty ACR instance, you will need to [push an image into ACR](https://docs.microsoft.com/azure/container-registry/container-registry-get-started-docker-cli) so that you can later configure your app to use it in [STEP 3](#step-3-configure-webapp-to-pull-imagetag-from-acr).

## Template Assumptions

- All Resource are in the same subscription
- Webapp and App Service plan are in the same resource group and location
-

## Template parameters

### Requiered Parameters

- **webAppName**: This is the name of your webapp, it should be globally unique
- **skuCode**: App Service Plan (ASP) pricing tier (default is P1v2 for production workloads)
- **location**: Azure region where the ASP and WebApp will be created
- **acrRG**: Resource Group for the target ACR
- **acrURL**: ACR URL (example: `myacr.azurecr.io` )
- **acrImage**: Image you want to pull
- **acrTag**: Tag you want to pull

### Optional Parameters

## Template Resources

The sample template will create 3 resources:

### App Service Plan

This section creates a new App Service plan resource, it uses the `hostingPlanName`, `location` and `skuCode` parameters.

``` json
{
  "apiVersion": "2018-11-01",
  "name": "[parameters('hostingPlanName')]",
  "type": "Microsoft.Web/serverfarms",
  "location": "[parameters('location')]",
  "properties": {
    "name": "[parameters('hostingPlanName')]",
    "reserved": true
  },
  "sku": { "Name": "[parameters('skuCode')]" }
}
```

### Webapp

This section creates the WebApp resource, it uses the `webAppName` and `location` parameters.

The system assigned managed identity is enabled through the idenity property:

> `"identity": { "type": "SystemAssigned" }`

The webapp is configured to present the system assigned managed identity for acrPull operations with the  `acrUseManagedIdentityCreds` property:

> `"acrUseManagedIdentityCreds": true`

The Webapp is assigned to an ASP through the `serverFarmId` property:

>`"serverFarmId": "[concat('/subscriptions/', subscription().subscriptionId,'/resourcegroups/', resourceGroup().id, '/providers/Microsoft.Web/serverfarms/', parameters('hostingPlanName'))]"`

Since the webapp needs to be linked to an ASP, we use the `dependsOn` clause to make sure the ASP is created first.

> ` "dependsOn": [ "[concat('Microsoft.Web/serverfarms/', parameters('hostingPlanName'))]" ],`

The reference the specific ACR instance  and what image and tag to pull are defined by the `linuxFXVersion` property.

> `"linuxFxVersion": "[variables('linuxFxVersion')]",`


``` json
{
      "apiVersion": "2018-11-01",
      "name": "[parameters('webAppName')]",
      "type": "Microsoft.Web/sites",
      "location": "[parameters('location')]",
      "identity": { "type": "SystemAssigned" },
      "tags": {},
      "dependsOn": [
        "[concat('Microsoft.Web/serverfarms/', parameters('hostingPlanName'))]"
      ],
      "properties": {
        "name": "[parameters('webAppName')]",
        "siteConfig": {
          "linuxFxVersion": "[variables('linuxFxVersion')]",
          "acrUseManagedIdentityCreds": true
        },
        "serverFarmId": "[concat('/subscriptions/', subscription().subscriptionId,'/resourcegroups/', resourceGroup().id, '/providers/Microsoft.Web/serverfarms/', parameters('hostingPlanName'))]"
      }
    },
```

### acrPull Role Assignment

acrPull is a built in role and it can be referenced through it's `roleDefinitionId`:

> "roleDefinitionId": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Authorization/roleDefinitions/', '7f951dda-4ed3-4680-a7ca-43fe172d538d')]",

We need to pass in the `principalId` for the system assigned identity that is created as part of the webapp, since this is not known at the start of the template execution we can use the reference syntax to query for it:

> `"principalId": "[reference(resourceId('Microsoft.Web/sites', parameters('webAppName')),'2019-08-01', 'full').identity.principalId]"`

``` json
{
    "type": "Microsoft.Resources/deployments",
    "apiVersion": "2020-10-01",
    "name": "acrPUll_Permission",
    "resourceGroup": "[parameters('acrRG')]",
    "properties": {
    "mode": "Incremental",
    "parameters": {},
    "template": {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
        "contentVersion": "1.0.0.0",
        "metadata": {},
        "parameters": {},
        "resources": [
        {
            "type": "Microsoft.Authorization/roleAssignments",
            "apiVersion": "2020-04-01-preview",
            "name": "[guid(concat('Microsoft.Web/sites/', parameters('webAppName')))]",
            "properties": {
            "roleDefinitionId": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Authorization/roleDefinitions/', '7f951dda-4ed3-4680-a7ca-43fe172d538d')]",
            "principalId": "[reference(resourceId('Microsoft.Web/sites', parameters('webAppName')),'2019-08-01', 'full').identity.principalId]",
            "principalType": "ServicePrincipal"
            }
        }
        ]
    }
    },
    "dependsOn": [
    "[concat('Microsoft.Web/sites/', parameters('webAppName'))]"
    ]
}
```

## Full Example

ARM tempaltes target a specific resource group (RG), the RG should exist before doing a deployment to it.

You can create a new RG using the [az group create](https://docs.microsoft.com/cli/azure/group?view=azure-cli-latest#az-group-create)  Azure CLI command:

```azurecli
az group create --name <rgName> --location <myLocation> -o none
```

To deploy the tempalte you can use the [az deployment group create](https://docs.microsoft.com/cli/azure/group/deployment?view=azure-cli-latest#az-group-deployment-create) command:

```azurecli
az deployment group create -g <rgName> --template-file <my_template_file.json> --parameters webAppName=<webAppName> acrURL=<acrURL> acrImage=<acrImage> acrTag=<acrTag> acrRG=<acrRG> location=<location> -o table
```


```json
{
  "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "webAppName": { "type": "string" },
    "hostingPlanName": {
      "defaultValue": "[concat('asp-', parameters('webAppName'))]",
      "type": "string"
    },
    "location": {
      "defaultValue": "CentralUS",
      "type": "string"
    },
    "skuCode": {
      "defaultValue": "P1v2",
      "type": "string"
    },
    "acrRG": {
      "type": "string"
    },
    "acrURL": {
      "type": "string"
    },
    "acrImage": {
      "type": "string"
    },
    "acrTag": {
      "type": "string"
    }
  },
  "variables": {
    "linuxFxVersion": "[concat('DOCKER|', parameters('acrURL'), '/', parameters('acrImage'), ':', parameters('acrTag'))]"
  },
  "resources": [
    {
      "type": "Microsoft.Resources/deployments",
      "apiVersion": "2020-10-01",
      "name": "acrPUll_Permission",
      "resourceGroup": "[parameters('acrRG')]",
      "properties": {
        "mode": "Incremental",
        "parameters": {},
        "template": {
          "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentTemplate.json#",
          "contentVersion": "1.0.0.0",
          "metadata": {},
          "parameters": {},
          "resources": [
            {
              "type": "Microsoft.Authorization/roleAssignments",
              "apiVersion": "2020-04-01-preview",
              "name": "[guid(concat('Microsoft.Web/sites/', parameters('webAppName')))]",
              "properties": {
                "roleDefinitionId": "[concat('/subscriptions/', subscription().subscriptionId, '/providers/Microsoft.Authorization/roleDefinitions/', '7f951dda-4ed3-4680-a7ca-43fe172d538d')]",
                "principalId": "[reference(resourceId('Microsoft.Web/sites', parameters('webAppName')),'2019-08-01', 'full').identity.principalId]",
                "principalType": "ServicePrincipal"
              }
            }
          ]
        }
      },
      "dependsOn": [
        "[concat('Microsoft.Web/sites/', parameters('webAppName'))]"
      ]
    },
    {
      "apiVersion": "2018-11-01",
      "name": "[parameters('webAppName')]",
      "type": "Microsoft.Web/sites",
      "location": "[parameters('location')]",
      "identity": { "type": "SystemAssigned" },
      "tags": {},
      "dependsOn": [
        "[concat('Microsoft.Web/serverfarms/', parameters('hostingPlanName'))]"
      ],
      "properties": {
        "name": "[parameters('webAppName')]",
        "siteConfig": {
          "linuxFxVersion": "[variables('linuxFxVersion')]",
          "acrUseManagedIdentityCreds": true
        },
        "serverFarmId": "[concat('/subscriptions/', subscription().subscriptionId,'/resourcegroups/', resourceGroup().id, '/providers/Microsoft.Web/serverfarms/', parameters('hostingPlanName'))]"
      }
    },
    {
      "apiVersion": "2018-11-01",
      "name": "[parameters('hostingPlanName')]",
      "type": "Microsoft.Web/serverfarms",
      "location": "[parameters('location')]",
      "properties": {
        "name": "[parameters('hostingPlanName')]",
        "reserved": true
      },
      "sku": { "Name": "[parameters('skuCode')]" }
    }
  ]
}
```
