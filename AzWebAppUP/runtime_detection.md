# Automatic Runtime Detection with `az webapp up`

The [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/?view=azure-cli-latest) includes a set of commands to manage Web App resources ([learn more](https://docs.microsoft.com/cli/azure/webapp?view=azure-cli-latest)). Included in this set of commands `az webapp up` bundles functionality to **create** a Web App and **deploy code** from a local workspace. The command is required to run from the folder where the code is present. Current support includes apps targeting:

- ASP .NET
- .NET Core
- Node
- Python

As part of the execution of `az webapp up` command it performs a **best effort** detection to match your code (in your local directory) with a supported runtime in your Web App.

The runtime detections logic uses the hints outlined below. Any code that doesn’t match this logic is blocked to avoid compatibility issues.

## Python detection logic

Python detection looks for the existence of `requirements.txt` in the current working directory.

## Node detection logic

Node detection looks for the existence of the `package.json` or `sever.js` or `index.js` in the current working directory.

## ASP .NET and .NET Core detection logic

ASP .NET and .NET Core detection is done by looking for the existence of `*.csproj` in the current working directory.

## Manual runtime definition

The runtime is a property of the web app used to host your code. If you want to set the runtime manually you can use the [az webapp create](https://docs.microsoft.com/cli/azure/webapp?view=azure-cli-latest#az-webapp-create) command.
