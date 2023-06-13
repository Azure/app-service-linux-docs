# Debian 9 End of Life

On June 30th 2022 Debian 9 (also known as "Stretch") will reach End-of-Life (EOL) status, which means security patches and updates will cease. As of June 2022, a platform update is rolling out to provide an upgrade path to Debian 11 (also known as "Bullseye"). The runtimes listed below are currently using Debian 9; if you are using one of the listed runtimes, follow the instructions below to upgrade your site to Bullseye.

- Python 3.8
- Python 3.7
- .NET 3.1
- PHP 7.4

> [!NOTE]
> To ensure customer applications are running on secure and supported Debian distributions, after February 2023 any Linux Web app that is targeting a supported runtime (not End of Life) and still running on Debian 9 (Stretch) will be upgraded to Debian 11 (Bullseye) automatically.
>

## Verify the platform update

First, validate that the new platform update which contains Debian 11 has reached your site.

1. In the azure portal, navigate to your app and select SSH 
1. From the SSH promt validate the platform version using the following command:  `printenv | grep PLATFORM_VERSION`
1. If the value of `PLATFORM_VERSION` starts with "99" or greater, then your site is on the latest platform update and you can continue to the section below. If the value does **not** show "99" or greater, then your site has not yet received the latest platform update--please check again at a later date.

Next, create a deployment slot to test that your application works properly with Debian 11 before applying the change to production.

1. [Create a deployment slot](deploy-staging-slots.md#add-a-slot) if you do not already have one, and clone your settings from the production slot. A deployment slot will allow you to safely test changes to your application (such as upgrading to Debian 11) and swap those changes into production after review. 
1. To upgrade to Debian 11 (Bullseye), create an app setting on your slot named `WEBSITE_LINUX_OS_VERSION` with a value of `DEBIAN|BULLSEYE`.

    ```bash
    az webapp config appsettings set -g MyResourceGroup -n MyUniqueApp --settings WEBSITE_LINUX_OS_VERSION="DEBIAN|BULLSEYE"
    ```
1. Deploy your application to the deployment slot using the tool of your choice (VS Code, Azure CLI, GitHub Actions, etc.)
1. Confirm your application is functioning as expected in the deployment slot.
1. [Swap your production and staging slots](deploy-staging-slots.md#swap-two-slots). This will apply the `WEBSITE_LINUX_OS_VERSION=DEBIAN|BULLSEYE` app setting to production.
1. Delete the deployment slot if you are no longer using it.

## Opt-out of the Debian 11 upgrade

To opt out of the automatic upgrade to Debian 11, you can set `WEBSITE_LINUX_OS_VERSION` to a value of `DEBIAN|STRETCH`.

```bash
    az webapp config appsettings set -g MyResourceGroup -n MyUniqueApp --settings WEBSITE_LINUX_OS_VERSION="DEBIAN|STRETCH"
```
**Note: Opting out of the upgrade will increase the startup time for your SCM site. You should do the above step only as a temporary measure while you upgrade your application to work with Debian 11**
## Resources

- [Debian Long Term Support schedule](https://wiki.debian.org/LTS)
- [Debian 11 (Bullseye) Release Notes](https://www.debian.org/releases/bullseye/)
- [Debain 9 (Stretch) Release Notes](https://www.debian.org/releases/stretch/)