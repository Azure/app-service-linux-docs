# How to: Avoid JBOSS clustering timeouts due to obsolete discovery files

During the normal lifecycle of your JBOSS EAP app there can be multiple events that can trigger your app to move across different nodes on the App Service infrastucture, this can be caused by user opertations, such as deployments, scale operations, etc... or platform maintenance oeprations.

Over time this will cause an acumulation of stale discovery files leading to potential timeouts for the cluster.

To avoid this the best practice is to include the cleanup of this stale files as part of the application startup using the JBOSS CLI.

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
