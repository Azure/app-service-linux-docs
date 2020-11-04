# Early Access Runtime

**Early Access** is a new feature of App Service that allows for the rapid delivery of updates and new versions of the programing languages/runtime and SDK supported by the platform. As a developer you will get access to the latest new releases, without having to wait for an App Service release cycle to include support.

This new features allows the service to decouple the release of new language support from the regular App Service platform updates. This is important because while App Service platform is updated on a regular cadence through the year (about once a month) framework and 3rd party releases don't follow the same schedule and can happen at any time.

**Early Access** will allow App Service to deliver updates in a matter of hours/days of new versions becoming publicly available in a fully supported way with little or no loss in functionality and support.

## How does Early Access work

There are 2 different implementations of this feature to address both Windows and Linux versions of App Service:

### Early Access on Windows

If your app is hosted on a Windows App Service plan and using an **Early Access** runtime, the specific instance where your app is running will get the necessary Runtime/SDK bits installed through a *Just In Time (JIT)* mechanism as part of the application initialization process (also known as *cold-start*).

### Early Access on Linux

If your app is hosted on a Linux App service plan it will be executed within a container that is provided by the platform and includes the necessary Runtime and SDK specified in your configuration. Versions of this containers are usually cached on each App Service region. **Early Access** images are not cached locally and will need to be pulled as part of the application initialization process (also knows as *cold-start*).

## Limitations of Early Access

An **Early Access** runtime has full platform support and full fidelity of features. In other words, they behave just like every other runtime supported by App Service.

**Early Access** does have an impact on *cold-start* performance and build times (if build is happening on App Service):

### Cold-start performance impact

An app using an **Early Access** runtime will have a slower initialization time compared to an app using a *built-in* runtime. Based on our testing the P95 impact is ~30 seconds with the average impact being <10 seconds. This impact applies once per instance and should not be observed on subsequent application restarts as long as they happen on the same instance.

### Build performance impact

An app using an **Early Access** runtime will have a slower build time compared to an app using a *built-in* runtime. Based on our testing the P95 impact on build is ~60 seconds with the average impact being <20 seconds. This impact applies once per instance and should not be observed on subsequent builds as long as they happen on the same instance.

## Upgrade from Early Access Runtime

Apps targeting **Early Access** runtime will be automatically upgraded to *built-in* versions as soon as the next App Service release reaches their app. This upgrade is no different from any other App Service updated that would regularly apply to your app and is transparent only resulting in eliminating the *cold-start* and build time performance impact of **Early Access** mechanism.
