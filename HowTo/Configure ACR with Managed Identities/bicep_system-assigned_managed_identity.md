# How to use Bicep Templates to configure your webapp to pull images from ACR using Managed Identities

This guide explains how to use Bicep templates to configure an Azure Web App to pull container images from Azure Container Registry (ACR) using either System-assigned or User-assigned managed identities. Using managed identities is a best practice as it allows for the principle of least privileged access compared to using admin accounts.

## Prerequisites

- An Azure subscription
- Azure CLI installed
- An existing Azure Container Registry (ACR) with a container image
- Basic knowledge of Bicep and Azure resources

## Overview

We'll cover two scenarios:
1. Using a System-assigned managed identity
2. Using a User-assigned managed identity

For both scenarios, we'll create an App Service Plan and a Web App configured to use a container image from ACR.

## Scenario 1: Using a System-assigned Managed Identity

### Bicep Template

Here's the complete Bicep template for configuring a Web App with a System-assigned managed identity:

```bicep
param webAppName string = uniqueString(resourceGroup().id)
param sku string = 'B1'
param location string = resourceGroup().location
param registryName string = 'myacr'
param imageFullName string = 'myimage:latest'

var appServicePlanName = toLower('AppServicePlan-${webAppName}')
var webSiteName = toLower('wapp-${webAppName}')

resource appServicePlan 'Microsoft.Web/serverfarms@2020-06-01' = {
  name: appServicePlanName
  location: location
  properties: {
    reserved: true
  }
  sku: {
    name: sku
  }
  kind: 'linux'
}

resource appService 'Microsoft.Web/sites@2021-01-01' = {
  name: webSiteName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      acrUseManagedIdentityCreds: true
      appSettings: []
      linuxFxVersion: 'DOCKER|${registryName}.azurecr.io/${imageFullName}'
    }
  }
}
```

### Key Points

1. The `appServicePlan` resource creates a Linux App Service Plan.
2. The `appService` resource creates the Web App with the following important properties:
   - `identity.type: 'SystemAssigned'`: This enables the System-assigned managed identity.
   - `siteConfig.acrUseManagedIdentityCreds: true`: This configures the Web App to use the managed identity for pulling images from ACR.
   - `siteConfig.linuxFxVersion`: This specifies the container image to use.

## Scenario 2: Using a User-assigned Managed Identity

### Bicep Template

Here's the complete Bicep template for configuring a Web App with a User-assigned managed identity:

```bicep
param webAppName string = uniqueString(resourceGroup().id)
param sku string = 'B1'
param location string = resourceGroup().location
param managedIdentityId string
param registryName string = 'myacr'
param imageFullName string = 'myimage:latest'
param managedIdentityClientId string

var appServicePlanName = toLower('AppServicePlan-${webAppName}')
var webSiteName = toLower('wapp-${webAppName}')

resource appServicePlan 'Microsoft.Web/serverfarms@2020-06-01' = {
  name: appServicePlanName
  location: location
  properties: {
    reserved: true
  }
  sku: {
    name: sku
  }
  kind: 'linux'
}

resource appService 'Microsoft.Web/sites@2021-01-01' = {
  name: webSiteName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      acrUseManagedIdentityCreds: true
      acrUserManagedIdentityID: managedIdentityClientId
      appSettings: []
      linuxFxVersion: 'DOCKER|${registryName}.azurecr.io/${imageFullName}'
    }
  }
}
```

### Key Points

1. The `appServicePlan` resource is the same as in the System-assigned scenario.
2. The `appService` resource has some differences:
   - `identity.type: 'UserAssigned'`: This specifies that we're using a User-assigned managed identity.
   - `identity.userAssignedIdentities`: This links the User-assigned managed identity to the Web App.
   - `siteConfig.acrUserManagedIdentityID`: This specifies the Client ID of the User-assigned managed identity to use for pulling images from ACR.

## Deployment

To deploy these Bicep templates, you can use the Azure CLI. First, create a new resource group (if needed):

```bash
az group create --name myResourceGroup --location eastus
```

Then, deploy the Bicep template:

```bash
az deployment group create --resource-group myResourceGroup --template-file ./template.bicep
```

## Additional Considerations

1. **Private ACR**: If your ACR is behind a private endpoint, you'll need to join the App Service to the vNet and add some additional configuration:

   ```bicep
   resource appService 'Microsoft.Web/sites@2021-01-01' = {
     // ... other properties ...
     properties: {
       virtualNetworkSubnetId: appServiceSubnetId
       siteConfig: {
         vnetRouteAllEnabled: true
         appSettings: [
           {
             name: 'WEBSITE_PULL_IMAGE_OVER_VNET'
             value: 'true'
           }
         ]
         // ... other siteConfig properties ...
       }
     }
   }
   ```

2. **Role Assignment**: Don't forget to assign the AcrPull role to your managed identity for the target ACR. This can be done using Azure CLI or by adding a role assignment resource to your Bicep template.

## Conclusion

Using Bicep templates to configure your Web App to pull images from ACR using managed identities provides a secure and scalable solution. By leveraging either System-assigned or User-assigned managed identities, you can avoid storing sensitive credentials and adhere to the principle of least privilege.

Remember to always use the latest API versions and consult the official Azure documentation for any updates or changes to these configurations.
