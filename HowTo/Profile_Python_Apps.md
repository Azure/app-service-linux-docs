# Azure Linux App Service – How to profile Python based App

> **NOTE**:
>
> - These instructions only apply to Linux based App Service.

Code Profilers helps in troubleshooting performance issues with App Services. They provide information on which line/function of the application is taking a long time to execute or utilizing a lot of compute resources.  This article explains how to code profile python apps hosted on Linux based App Services. 

## Prerequisites:

VizTracer is an open-source tool which is a low-overhead profiling tool that can trace and visualize your python code execution. This tool is available out of the box with App Service Python runtime. 

## Configure App for Profiling:

### Method 1: Profile specific blocks of code
1.	Include viztracer package in requirements.txt file 
  
2.	Update the source code to start and stop profiler wherever needed. 
  
3.	Redeploy the code 
    To do this from VSCode, 
    a.	Install AppService Extension 
    b.	Click on Azure Icon 
  
4.	Right click on the App Service name and click Deploy to WebApp 
   
5.	Reproduce the issue and review the traces 
  
 ### Method 2: Profile the entire application 
Note: This method can be used only if the python application is not using SIGUSR1 and SIGUSR2 signals. 
1.	Include viztracer package in requirements.txt file 
  
2.	Update the source code to add SIGUSR signal handler which can help with remote attach. 
  
3.	Redeploy the code  
    To do this from VSCode:
    a.	Install AppService Extension 
    b.	Click on Azure Icon 
    c.	Right click on the App Service name and click Deploy to WebApp 
  
4.	Start the profiler whenever needed and reproduce the issue. 
    a.	Navigate to WebSSH from Kudu site 
    (e.g. https://<webapp-name>.scm.azurewebsites.net/newui/webssh )    
    b.	Run ps -ax to identify the Process Id (PID) 
    c.	Run the following command 
        viztracer --attach <PID> -t <Number of seconds to profile> 
 
5.	Review the traces 
  
 
 ### Review Traces: 
1.	Ensure Python is installed in you Linux machine / Windows Subsystem for Linux (WSL) 
2.	Run the following command: 
    a.	pip install viztracer 
3.	Navigate to file manager of Kudu site of the App Service  
    a.	(e.g. https://<webapp-name>.scm.azurewebsites.net/newui/fileManager ) 
4.	Navigate to /home/LogFiles and download profiler_trace.json 
5.	In your local machine (Linux / WSL), run the following command 
        vizviewer profiler_trace.json 
  
We can view the results as flamegraph also using the command 
vizviewer --flamegraph profiler_trace.json 
 
  

