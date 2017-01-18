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
    {'guid': ..., 'value': ...}
]

### List of transactions

/v1/transactions

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

The message:
"Your user account has not been activated to add financial account."
 
 on "/add_bank" and "/add_lender" pages means that user not created yet in Atrium.

### Share change between all debt accounts.

1) The share is in percentage.
2) First account will get 100% by default.
3) All next accounts will get 0% by default.
4) User is able to assign any value in dashboard.
5) The sum of share of all debt accounts should be equal 100%.

### Dwolla mode.

sandbox / prod
Set on server for API.
Set on React in configureStore (dwolla.js depends on mode)

### Add bank

After adding bank successfully, member has status COMPLETED,
but accounts and transactions still processing by celery task
and not ready yet.

So, after a few minutes user need to refresh site or create 
some scheduler that will request accounts and transactions
(will increase load to API)

Or consider Web Sockets.
But not for MVP.

### Testing add bank in sandbox.

Bank name: MX Bank
Username: test_atrium
Password: any

To test Challenges:
Password: challenge
Correct answer: correct

### Testing add funding source to Dwolla in sandbox.

After user has been sign up to system, Dwolla customers created
in background. User profile should look like real profile with good data.
Otherwise, Dwolla customer can not be created.

As soon as Dwolla customer is created, and user has accounts, frontend will have link to create funding source.

### Transfers TDD
donkies/tests/transfers/README.md

### Transfer flow.

First we collect roundup to TransferPrepare.
Then from TransferPrepare total user's roundup amount processed to TransferDonkies model (if user set funding source account).
Then from TransferDonkies model we send transfer to Donkies LLC (via Dwolla).
As soon as money received by Donkies LLC (checked by API), we process received amount to debt user's accounts to TransferUser model.

From TransferUser model currently send cheques manually.
