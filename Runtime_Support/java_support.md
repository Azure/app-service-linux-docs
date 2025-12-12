# Java on App Service

For information on our update, support, and runtime retirement policies, please refer to the the official [App Service documentation page for Java](https://learn.microsoft.com/azure/app-service/language-support-policy?tabs=linux#java-specific-runtime-statement-of-support).

## How to update your app to target a different version of Java

> **NOTE**:
> Changing the stack settings of your app will trigger a re-start of your application.

You can change the runtime throgh the Azure portal:

1. In the Azure portal, click the **App Service** blade. Select the app you want to update.
2. Navigate to the Configuration blade under Settings of your App Service.
3. Find the **Stack settings** tab.
3. Click the drop-down menu under **Major version** (Linux) or **Java version** (Windows) and select the Java version you want (we recommend choosing the most recent version).
4. Click **Save**.
