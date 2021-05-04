# How to use system-assigned Managed Identities with App Service and Azure Container Registry

>**NOTE**:
>
> - This instructions only apply to Linux based containers configurations.
> - The Webapp and the Azure Container registry must be on the same azure subscription
>   - Accessing an a container registry on a different subscription is currently **not supported**.
> - The Azure Container registry must be internet accessible.
>   - Pulling container images through a Private Link / Private endpoint connection is currently **not supported**.
>

App Service can use **system-assigned** [managed identities](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview) to authenticate against **Azure Container Registry (ACR)** and perform `docker pull` operation.

Using **managed identities** is a best practice because they allow for the principle of *least privileged* access to be followed compared to using the **admin** accounts.

## Prerequisites

This guide uses the [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli?view=azure-cli-latest) to configure your resources. If you don't want to install the Azure CLI locally, you can always use [Azure Cloud Shell](https://docs.microsoft.com/azure/cloud-shell/quickstart).

## STEP 0 create your resources

> **Note:** If you already have resources you want to use, skip to **Step 1**

For this example we will need to create the following resources:
  
- Web App
- App Service Plan
- Azure Container Registry

``` bash
# Modify for your environment
$location="westus"
$RG_Name="SA-TEST-RG"
$ASP_Name="SA-TEST-ASP"
$Web_Name="SA-TEST-WEB-101"
$ACR_Name="satestacr"

#Create resources
az group create -n $RG_Name -l $location -o none
az acr create -n $ACR_Name --sku standard -g $RG_Name -l $location -o none
az appservice plan create --is-linux -n $ASP_Name --sku p1v2 -g $RG_Name -l $location -o none
az webapp create -n $Web_Name -g $RG_Name -p $ASP_Name -i "nginx" -o none

#List resources in the resource group
az resource list -g $RG_Name -o table
```

>**Note:** If you are starting with an empty ACR instance, you will need to [push an image into ACR](https://docs.microsoft.com/azure/container-registry/container-registry-get-started-docker-cli) so that you can later configure you app to use it.

## STEP 1: Assign an identity to your WebApp

This step will configure the webapp to use a system-assigned identity. System-assigned identities are created on the fly and unlike 'service-principle' they don't require you to be a subscription level admin to create and use them.

```bash
# Modify for your environment
Webapp_Config=$(az webapp show -g $RG_Name -n $Web_Name --query id --output tsv)"/config/web"

#Assign managed-identity to webapp
az webapp identity assign -g $RG_Name -n $Web_Name --identities $Identity_ARMID -o none

#Configure WebApp to use the Manage Identity Credentials to perform docker pull operations
az resource update --ids $Webapp_Config --set properties.acrUseManagedIdentityCreds=True -o none

```

## STEP 2: Grant access to the identity on ACR

This step will register the identity with ACR and grant it the minimum permission necessary for a webapp to pull and host containers from it.

``` bash
# Modify for your environment
Identity_ID=$(az identity show -g $RG_Name -n $ID_Name --query principalId --output tsv)
ACR_ID=$(az acr show -g $RG_Name -n $ACR_Name --query id --output tsv)

#ACR will allow the identity to perform pull operations and nothing more
az role assignment create --assignee $Identity_ID --scope $ACR_ID --role acrpull -o none
```

>NOTE: There can be some delay while a system-assigned managed-idenity is propagated through your AAD Tenant. If the `az role assignment create` fails wait and retry after a few min
>

## Step 3: Configure WebApp to pull image:tag from ACR

This step will configure the webapp to point to ACR and the Image:Tag for the container you want to use.

```bash
# Modify for your environment
ACR_URL=$(az acr show -g $RG_Name --n $ACR_Name --query loginServer --output tsv)
Image="myapp:latest"
FX_Version="Docker|"$ACR_URL"/"$Image

#Configure the ACR, Image and Tag to pull
az resource update --ids $Webapp_Config --set properties.linuxFxVersion=$FX_Version -o none --force-string

```
