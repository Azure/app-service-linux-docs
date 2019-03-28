This is the updated version to the original blob post by Sunitha Muthukrishna.  

There are several forms of WordPress running on App Service, but we recommend “WordPress on Linux” and “WordPress on Windows” from the Azure Marketplace as your start point. Because these Marketplace offerings are optimized for App Service, they are designed to be easy-to-install and come with the up-to-date software packages, and also with support from App Service team. Today, thousands of customers are running their WordPress sites on our Marketplace offerings.

While the Marketplace image comes with a fresh install of WordPress, customers can replace the code on the Web App and bring their own WordPress codebase (for example during migrations from on-premise or other platforms). Simply connect to the Web App using FTPS and replace the contents of the /home/site/wwwroot directory. Make sure to update the wp-config.php file with the correct database connection string, looking at the wp-config.php file that came with the Marketplace image as example.  For cases in which additional PHP extensions are needed for plugins or themes, we recommend customers to customize the Marketplace Docker image, add what’s needed, and run it on Web App for Containers, then migrate their site so that they don’t have to start from scratch.

One of most frequently asked questions by Azure App Service customers is how to speed up the WordPress site hosted on App Service.  Slow page load times can impact your target user audience and discourage them from visiting your website again. A lot of search engines consider page load times as well when ranking results and can impact the visibility of your website on their search engine results.  Before we discuss what steps to take to speed up your web application , lets understand some key design elements in App Service that may contribute to the latency. Here are two key design elements in App Service that can add latency to a page request:
•	App Service uses Azure Storage as the persistent storage for Web Apps, WordPress is installed on the persistent storage by default.
•	If you are not using MySQL in-app feature (Windows only) , then any other MySQL solution used with Web App is not living on the same virtual machine 
Consider implementing these quick and easy steps mentioned below to speed up your application. If not called out specifically, the best practices below apply to WordPress hosted on both Linux and Windows.
1. Web site and Database must be in the same data center
It seems obvious. When running your WordPress site on Azure App Service, make sure your database and website are in the same Azure region. Network latency can increase the page load time for your website if the site needs to go around the world to make a call to the database. Keeping the site and database components in the same data center will reduce the network latency and improve the page load time for your website. When you create a WordPress site using our Marketplace offerings, we automatically select the database in the same region as your Web App. If you choose to use a different database, please double check the connection string in wp-config.php to ensure your database is in the same region as your Web App. 
2. Use right MySQL database solution for your web app needs 
Investigate with one of these solutions is right for your database. Investigate and test out your application with these solutions to see the best fit which gives better performance.
•	Azure Database for MySQL (default option). Azure MySQL is the managed service for MySQL server on Azure, it supports SKU options to meet various performance, scale and price needs. Please choose the SKU according to your business needs. 
•	MySQL in-app (Windows only) which provides you a MySQL instance running on the same instance with your app and shares resources from the App Service plan. Note that apps using MySQL In App are not intended for production environments, and they will not scale beyond a single instance. 
3. Optimize your database
WordPress auto-saves everything but the disadvantage with this is that your database gets filled with a lot of post revisions, trackbacks, pingback, comments and trash items quickly which needs to be cleaned up manually on a regular basis. With the database plan you are using with your Website there will be limitation to the storage size allocated to your database and you may hit this limit as well if the database is not cleaned up regularly. WP-Optimize is a great plugin which allows you to routinely clean up your database making the database more efficient and filled only with what needs to be kept. It saves you a lot of time without doing manual queries to optimize and clean up your database.
4. Caching
If you start seeing a surge of user traffic hitting your site, you should consider adding some form of caching for your site to handle the spike of traffic. 
•	WordPress on Windows
•	IIS output caching :It’s easy to configure and setup. It significantly improves site throughput but may prevent confirmation messages from showing up when submitting comments. To learn more about IIS output caching, click here.
•	WP Super cache :It significantly improves site throughput and correctly handles comments submissions and other visitors’ actions. It slightly more complex to setup and configure than compared to IIS output caching. To learn more about Super cache configuration on IIS click here.
•	App Service Dynamic Cache turn on the Dynamic cache to improve performance. 
•	Wincache : Create a .user.ini under wwwroot of your web application to add additional PHP settings.  Enable wincache settings in a .user.ini wincache.fcenabled = 1 and wincache.reroute_enabled =1
•	Redis cache : Azure redis cache can also be integrated with WordPress with the help of WP redis plugin to get better performance. 
WordPress on Linux
Redis cache: the redis cache plugin is installed by default, you can activate the plugin and connect it to database to improve the performance. 
5. Always-on
For low traffic web site,  you can enable AlwaysOn to keep your web app always loaded.
6. Compress Images
If your WordPress site heavy with images, then images can take up most of bandwidth for your site. A couple of things you can do in this case:
•	Store all your media content in an Azure Storage Blob: Use Azure Storage Plugin which allows your website to store any new content to Azure storage instead of uploads directly of your WordPress site. If your site is media content heavy, it can significantly help to use an Azure CDN with the Azure Storage to reduce bandwidth.  
•	For Linux site, you can also mount additional storage accounts to the container which runs your WordPress site, you can use the additional storage for content and media files.
•	Compress the images: WP Smush.it is a great plugin that automatically compresses images as you upload them to the media library. There is no data loss during compression and you won’t see any difference in the quality of images. If you have thousands of images are saved in your media library, you can run them all through the plugin, compressing them to a manageable size.
7. Reduce HTTP requests
Every website make multiple dependent requests either to JS, CSS files or third party services or libraries. Putting all JavaScript into one JavaScript file and all CSS in one CSS file is considerably more efficient and reducing the dependent requests wherever possible can help. For CSS/JS scripts you can run a minify plugin like Better WordPress Minify which will combine all of your style sheets and JavaScript files into one hence reducing the number of requests that the browser needs to make. If your site uses third party libraries, it’s better to copy them locally them to make a call to the service that offers the library to reduce bandwidth.
8. Use Azure CDN
If the slowness can be diagnosed as a result of static content taking a long time to load , then use IIS Static content caching or Azure CDN .  
9. Diagnose if your theme is slowing down your site
Some themes just like plugins can be poorly written and can slow down your site. Test if your theme is responsible for the long page load times. To do this revert to the default WordPress template TwentyFourteen and check if the page load time is much better. If yes, then the Theme could be the culprit. To resolve this pick another theme. If there is no difference in the page load time after reverting the Theme to an older version, the try some of the tips listed in this blog.
10. Diagnose if any plugin is slowing down your site
Some plugins can be the culprit in slowing down your site especially if they are poorly written or configured. Use a plugin like P3 to understand how much all the plugins used by the application do impact your page load time in order to take necessary actions to speed up your site If there are unused plugins, this can add to you page load time as WordPress tries to load all the activated plugins. Clean up or remove all the plugins that are not being used. Used only the plugins that can improve your website and not drag out the performance of your site.
We have seen at least two plugins being slow on the App Service platform including Captcha and Visual composer. Find appropriate replacements of these plugins. 
11. Turn off Pingbacks and Trackbacks if you don't use it
WordPress uses Pingbacks and trackbacks methods to alert other blogs that your posts link to.
•	A pingback is a type of comment that’s created when you link to another blog post where pingbacks are enabled.
•	Trackbacks are a way to notify legacy blog systems that you’ve linked to them.
They can be a drain the page speed and are usually better turned off if you don’t really need them. To learn more about Pingbacks and Trackbacks, click here.
12. Specify Image dimension
Before the content is displayed to the end user, the browser had to identify the layout of the content around the images. Not knowing the size of the images, the browser has more work to do figure this out and take longer. It a best practice to specify image dimensions which saves the browser from having to go through this step, speeding things up.
All these optimizations are just a few minutes of work and help you see drastic improvement in the performance of your website.


