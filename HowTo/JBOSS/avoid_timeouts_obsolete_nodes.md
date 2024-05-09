# How to: Avoid JBOSS clustering timeouts due to obsolete discovery files

During the normal lifecycle of your JBoss EAP web app multiple events that can trigger your app to move across different nodes on the App Service infrastructure. This can be caused by user operations (such as deployments), scale operations, and platform maintenance operations.

Over time this will cause an accumulation of stale cluster discovery files leading to potential timeouts during startup. To avoid this scenario, the best practice is to include the cleanup of this stale files as part of the application configuration using the JBoss CLI.

> [!NOTE]
> Please note that this setting is now enabled by default in JBoss 7.4.7 and later in Azure App Service.
>

To do you should include 2 new files with your solution `/home/site/scripts/startup.sh` and `/home/site/scripts/config.cli`. You can also add this to your existing startup file if you already have one.

The contents of /home/site/scripts/startup.sh are as follows:

``` bash
#!/usr/bin/env bash

$JBOSS_HOME/bin/jboss-cli.sh -c --file=/home/site/scripts/config.cli
# end of file
```

The contents of /home/site/scripts/config.cli are as follows:

``` bash
/subsystem=jgroups/stack=tcp/protocol=FILE_PING/property=remove_all_data_on_view_change:add(value=true) 
# end of file
```
