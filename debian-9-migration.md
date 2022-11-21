# Debian 9 End of Life

On June 30th 2022 Debian 9 (also known as "Stretch") reached End-of-Life (EOL) status, which means security patches and updates have ceased. As of June 2022, a platform update is rolling out to provide an upgrade path to Debian 11 (also known as "Bullseye"). The runtimes listed below are currently using Debian 9; if you are using one of the listed runtimes, follow the instructions below to upgrade your site to Bullseye.

- Python 3.8
- Python 3.7

> [!NOTE]
> To ensure applications are running on secure and supported Debian distributions, after February 2023 all Linux web apps still running on Debian 9 (Stretch) will be upgraded to Debian 11 (Bullseye) automatically.
>
## Upgrade to Debian 11 using Deployment Slots

Create a deployment slot to test that your application works properly with Debian 11 before applying the change to production.

1. [Create a deployment slot](https://learn.microsoft.com/en-us/azure/app-service/deploy-staging-slots#add-a-slot) if you do not already have one, and clone your settings from the production slot. A deployment slot will allow you to safely test changes to your application (such as upgrading to Debian 11) and swap those changes into production after review.
2. To upgrade to Debian 11 (Bullseye), create an appsetting on your slot named `WEBSITE_LINUX_OS_VERSION` with a value of `DEBIAN|BULLSEYE`. You can use [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli) to set the appsetting.

    ```bash
    az webapp config appsettings set --name <app-name> --resource-group <resource-group-name> --settings WEBSITE_LINUX_OS_VERSION="DEBIAN|BULLSEYE"
    ```

3. Deploy your application to the deployment slot using the tool of your choice (VS Code, Azure CLI, GitHub Actions, etc.)
4. Confirm your application is functioning as expected in the deployment slot.
5. [Swap your production and staging slots](https://learn.microsoft.com/en-us/azure/app-service/deploy-staging-slots#add-a-slot#swap-two-slots). This will apply the `WEBSITE_LINUX_OS_VERSION=DEBIAN|BULLSEYE` app setting to production.
6. Delete the deployment slot if you are no longer using it.

## Upgrade to Debian 11 without Deployment Slots

1. To upgrade to Debian 11 (Bullseye), create an appsetting on your website named `WEBSITE_LINUX_OS_VERSION` with a value of `DEBIAN|BULLSEYE`. You can use [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli) to set the appsetting.

    ```bash
    az webapp config appsettings set --name <app-name> --resource-group <resource-group-name> --settings WEBSITE_LINUX_OS_VERSION="DEBIAN|BULLSEYE"
    ```

2. Redeploy your website using the tool of your choice (VS Code, Azure CLI, GitHub Actions, etc.)
3. Confirm your application is functioning as expected.

## Resources

- [Debian Long Term Support schedule](https://wiki.debian.org/LTS)
- [Debian 11 (Bullseye) Release Notes](https://www.debian.org/releases/bullseye/)
- [Debain 9 (Stretch) Release Notes](https://www.debian.org/releases/stretch/)
