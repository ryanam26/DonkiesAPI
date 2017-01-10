###  List of accounts

/v1/accounts     GET    

### List of credentials for institution

/v1/credentials/:institution_code

###  List of members

/v1/members     GET    

### Create member

/v1/members     POST    

Params:

institution_code

Array of required credentials for institution:
[{field_name: value}, ...]

Returns: member

#### Instruction for frontent.

After frontend sends request to create member, member created real-time (not in background) and returned to frontend.
Fronend knows all member's fields.
In the background backend tries to get member status.
As soon as status received - it is saved to database.

Frontend needs to call member detail endpoind (for example every 2 seconds) until it gets COMPLETED or CHALLENGED or SOME ERROR status.

If member status is CHALLENGED, member detail will contain list of challenges, that should be send to backend.

As soon as user filled all required challenges, frontend send data to resume member endpoint.


### Get member (Member detail endpoint) 

/v1/members/:identifier  GET

Member object.
Can get status of member using this endpoint.
Member object will contain atrium status and aggregated status.

### Resume member

/v1/members/resume/:identifier  POST

Param: "challenges": list of challenges.
Example: challenges = [
    {'label': ..., 'value': ...}
]

### List of transactions

/v1/transactions

### Pytrium

It seems there is some bug in Pytrium.
When I test separately respond on challenge with incorrect answer and correct answer, they works fine. When one after another - get error. But probably because it is the same test session and maybe on production that bug won't appear.

Incorrect answer produce DENIED status.
Correct answer produce COMPLETED status.

### settings/data.json (that in gitignore) looks:

Instead of *** - real credentials.

{
    "ALLOWED_HOSTS": ["*"],
    "SECRET_KEY": "***",
    "DB_NAME": "donkies",
    "DB_USER": "udonkies",
    "DB_PASSWORD": "***",
    "DB_HOST": "127.0.0.1",
    "SERVER_IP": "159.203.137.132",
    "SOCIAL_AUTH_FACEBOOK_KEY": "***",
    "SOCIAL_AUTH_FACEBOOK_SECRET": "***",
    "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY": "***",
    "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET": "***",
    "SOCIAL_AUTH_TWITTER_KEY": "***",
    "SOCIAL_AUTH_TWITTER_SECRET": "***",
    "ATRIUM_CLIENT_ID_DEV": "***",
    "ATRIUM_KEY_DEV": "***",
    "ATRIUM_CLIENT_ID_PROD": "***",
    "ATRIUM_KEY_PROD": "***"
}

### Possible transfer scenarios (info from forum)

Account -> unverified Customer
Account -> verified Customer
Account -> receive-only Customer
unverified Customer -> verified Customer
verified Customer -> verified Customer
verified Customer -> unverified Customer

### Nginx

server {
    server_name  dev.donkies.co;
    listen 80;
    charset utf-8;
    access_log  /var/log/nginx/sites/access/donkies_frontend.log;
    error_log   /var/log/nginx/sites/error/donkies_frontend.log crit;

    access_log off;
    root /home/alex/dj/donkies/donkies/react/dist;

    if ($host = 'www.dev.donkies.co' ) {
        rewrite  ^/(.*)$  https://dev.donkies.co/$1  permanent;
    }

    location /account {
        autoindex off;
        try_files $uri  $uri/ /index.html;
    }

    location ^~ /static {
        autoindex off;
        root /home/alex/dj/donkies/static;
    }

    # Attempt to load static files, if not found route to @rootfiles
    location ~ (.+)\.(html|json|txt|js|css|jpg|jpeg|gif|png|svg|ico|eot|otf|woff|woff2|ttf)$ {
        try_files $uri @rootfiles;
    }

    # Check for app route "directories" in the request uri and strip "directories"
    # from request, loading paths relative to root.
    location @rootfiles {
        # rewrite ^/(?:some|foo/bar)/(.*) /$1 redirect;
        rewrite ^/(.*)/(.*)  /404 redirect;
    }

    location = / {
        uwsgi_pass 127.0.0.1:4442;
        include uwsgi_params;
        uwsgi_buffers 8 128k;
    }
}

### js/app.js of Material Admin

All changes in file react/dist/js/app.js
This is working project's file of template.


### Frontend

On first load of dashboard in App container load accounts and transactions
from server to Redux state.
