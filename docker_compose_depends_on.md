# Docker Compose depends_on option

In Docker Compose, depends_on can only control the start and stop of containers in dependency order. However, for startup Compose does not wait until a container is “ready” (whatever that means for your particular application). Docker published this [best practice for controlling startup and shutdown order in Compose](https://docs.docker.com/compose/startup-order/).

## App Service Multi-container Web App Best Practice

[App Service multi-container (preview)](https://docs.microsoft.com/azure/app-service/containers/tutorial-multi-container-app) doesn’t support the depends_on option in Docker Compose configuration, we would ignore the option if customer specifies it in the Docker-Compose yaml file. Similar to what is recommended by Docker, we recommend App Service customers to handle the dependencies by performing the check in your application code, both at startup and whenever a connection is lost for any reason. Design your application to attempt to re-establish a connection to the database after a failure. If the application retries the connection, it can eventually connect to the database.

For example, in this Python/Redis case, Python code retries connection to Redis for 5 times before it errors out. You can get the full source repo on [Github](https://github.com/yiliaomsft/compose-redis).  

``` yaml
import time

import redis
from flask import Flask

app = Flask(__name__)
cache = redis.Redis(host='redis', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello from Azure App Service team! I have been seen {} times.\n'.format(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
```
