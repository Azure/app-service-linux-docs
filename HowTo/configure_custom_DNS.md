# How To - Use a custom DNS nameserver with your app

This article shows you how to configure your apps to use a custom DNS name server for outgoing connections. Some of the features in App Service will change how outgoing DNS queries are resolved for your apps. This article is intended to help you understand how can DNS configurations change for your app how you can override and use a custom DNS.

## Default behavior

In App Service, the default the outgoing DNS name server is [Azure DNS](https://azure.microsoft.com/services/dns/). The address for Azure DNS is `168.63.129.16`.

### Apps in a VNet Integration

 When your app is configured to use the [VNet Integration](https://docs.microsoft.com/azure/app-service/web-sites-integrate-with-vnet) feature, it will inherit the DNS configuration from the VNET. [Learn more: Name resolution for resources in Azure virtual networks](https://docs.microsoft.com/azure/virtual-network/virtual-networks-name-resolution-for-vms-and-role-instances).
  
### Apps in an App Service Environment

Apps in an [App Service Environment](https://docs.microsoft.com/azure/app-service/environment/intro) are in a VNet by default and will use the **DNS name server** configuration of the VNet.

### Apps using Hybrid Connections

Apps using [Hybrid Connections](https://docs.microsoft.com/azure/app-service/app-service-hybrid-connections) will use **Azure DNS** for most name resolution queries. The exception to this is when reaching resources across the hybrid connection since the configuration is a well-defined FQDN and port combination.

An app can be configured to use both VNet integration and Hybrid Connections in this scenario the DNS configuration for the VNet will be used except for traffic going across the hybrid connection.

> [!Warning]
>
> - For Linux Apps, if you modify the /etc/resolv.conf to use another Nameserver manually, this will break Hybrid Connection resolutions.
> - Windows container apps currently do not support Hybrid Connections
>

## Override DNS

If you need to use a custom DNS on a per app basis, you can use **App Settings**. App Setting will take precedence over any alternate configuration.

|App Setting| Purpose |
|:--|:--|
|`WEBSITE_DNS_SERVER`|Primary Nameserver|
|`WEBSITE_DNS_ALT_SERVER`|Fallback Nameserver|

> [!Note]
> Overriding the DNS configuration is not currently supported for Linux apps in the VNET Integration Scenario.

## Troubleshooting

From the app console, you can check for the result returned by your configured DNS name server. On Linux, you can do this using `nslookup`. This command will always return what your app is configured with. On Windows, you need to use the command `nameresolver`. If you use `nslookup` on a Windows app, you'll always resolve against Azure DNS.
