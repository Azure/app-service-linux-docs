# Changing MySQL database password

WordPress deployment creates an AppService and a MySQL flexible database server under the same resource group. Login credentials for the MySQL server are generated randomly during deployment process. 
 
These database connection details are configured into WordPress via **Application Settings** option available in the AppService. You can retrieve the database connection details from Application Setting section in case you forgot to note them down during the creation time. 

Please note that the Application Settings related to database connection are **persistent** during the entire lifetime of your WebApp. Any changes to these settings will reflect the same in your WordPress application.

|    Application Setting Name    |
|--------------------------------|
|    DATABASE_NAME               |
|    DATABASE_HOST               |
|    DATABASE_USERNAME           |
|    DATABASE_PASSWORD           |



### Changing MySQL Database Password

First, go to the MySQL resource corresponding to your WordPress deployment, and click on **Reset Password** option as shown below. Now enter the new password and click on Save. Wait until the action is completed. 

Then navigate to the Configuration section of your AppService and update the **DATABASE_PASSWORD** Application Settings in your AppService. Once you update the value, click on Save and wait for app to get restarted. 

<br>
<kbd><img src="./media/changing_mysql_password_1.png" width="1000" /></kbd><br>
<kbd><img src="./media/changing_mysql_password_2.png" width="1000" /></kbd>
