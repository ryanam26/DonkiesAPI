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


### Credentials

Credentials can be stored in database, then Celery task will need to update them constantly. Or they can be requested from Atrium on demand.

The current implementation - request on demand.


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

### Transfers TDD
donkies/tests/transfers/README.md

### Transfer flow.
Instructions in TransferPrepare and TransferDonkies model.

### User flow

1) User sign up. After sign up user will get email where it should confirm registration. After confirmation user.is_confirmed = True. If user sign up by facebook, it confirmed automatically.

2) After user is created in database it automatically created in Atrium. As we use production Atrium, do not create fake users.

3) User need to add bank accounts (members). As soon as members are created, celery task automatically will fetch all accounts and transactions for these members.

4) Then user need to set funding source. But customer in Dwolla will be created only after user has completed profile. So, the next step, user should complete profile. As soon as profile completed, celery task will create customer in Dwolla. On Sandbox Dwolla user data can be fake, but it should looks like real, otherwise customer can not be created.

5) User need to add funding source (via IAV)

6) In settings User set minimum_transfer_amount (By default $5 and can be changed in settings). As soon as collected roundup >= minimum_transfer_amount celery tasks will automatically send transfer to Donkies LLC in Dwolla. Donkies LLC email is used as a destination in Dwolla. 

7) After Donkies LLC got transfer, it needs to send transfer to user. Celery task will update data and TransferUser model will contain debt accounts and amounts to send.

8) Send money to user's debt accounts from TransferUser model. (Currently manually)
