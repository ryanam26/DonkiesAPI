# Donkies REST API

Technologies:
- Python >= 3.5
- Django >= 1.10
- Django REST Framework >= 3.4.6
- Celery >= 4.0
- Posgres >= 9.6
- RabbitMQ or Redis
- Pytrium >= 0.1.2 (Financial Transaction API)


Requirements:
This project will be a REST based API created using Django REST Framework (DRF).
Eventually, this API will be consumed by a Front-End javascript based app.
Usernames and passwords will never be stored for third party services. We will only store usernames and
passwords for users that have chosen to manually register with this API.

This is the process flow and functionality requirements for the application:

## Phase 1:
1. Front-End app will route users to a login page managed by this system
    1. The login page will allow users to create an account using a form, Facebook, or Gmail account.
        - For manual sing up all that will be required is:
        First name, last name, email address, birthday
        - For Facebook or Gmail accounts:
        Extract as much information as possible from the third part service.
        Data can be stored into a field in JSON format... however separating the information into multiple fields may make more sense. However, this is will be decided by the developer.
        - The current REST API links a Django User to the app's user model that is called DonkiesUser. This may not be the best approach. This can be changed if there is a more secure and better approach.
    2. Once user is created and authenticated then system will route back to the front end app's URL/URI. This URL/URI must be registered with the backend system... this is in order to prevent unauthorized app from accessing tokens and user information. The project is currently using Django oAuthToolkit for this process.
    3. The frontend will exchange an access token for the user tokens in order to access system. At this point, any action performed on the frontend should be tied to the authenticated user.

2. Authenticated users will be able to link a "bank account". I am not sure how to make this secure. Users will need to provide their bank account username and password... if the frontend app is going to be collecting the information and then sending it to the backend then we need to make sure the frontend is trusted. I am leaving how to do this up to the developer. Maybe the frontend API can load a modal that's generated with the backend? I know the transaction API provides a javascript app for registering bank accounts so maybe that can be used.
    1. When a user provides his username and password, the backend system will use it to establish an account with the transaction API we're using. The company we're using for the transactions is called MX. Information on the API can be found at: https://atrium.mx.com/documentation# Please take a look at this company's login javascript... maybe this is something the backend can provide to the front end. The access tokens for this API are currently contained in this project.
    2. The frontend will poll the backend (once a second) to see if the bank account was linked successfully or not. The backend will provide the status of the link (link_status) to the front end. The possible status will be:  
        - Success
        - Processing
        - Wrong Username/Password
        - Challenged
        - Other Error (basically the server isn't working for some reason... for this case an entry for LinkedBankAccount should have even been generated)
    3. If "wrong username/password" there the backend should allow the front end to change the username and password for the user and try again.
    4. If "challenged", the backend should provide a way for the front end to access the "challenge" question and then a way to post the response to the challenge... The backend should then continue to "Processing" state...
    6. If "success", the front end app will move the user to the next step of the front end flow. The backend should continue through the the backend process and download all the transactions from the account. Again, all the data can be placed into model fields or into a field as a JSON object. I leave this decision up to the developer. I think having some of the information as fields will help the app scale up better. While the backend is storing all the transaction data, it should set the "LinkedBankAccount" model's transactions_status field to "downloading". If complete, then the backend should record the datetime of when it completed in a field called last_synced. The possible values for transactions_status should be,
        - downloading
        - failed
        - complete

# Landing Page
When user arrives to website, he will see a landing page that contains a login/register button. 

![alt tag](https://github.com/aeria-io/DonkiesRestAPI/blob/master/readme_assets/Landing-1.png)

# Login or Register
Ideally this should appear as a modal on the main landing page. This window should provide a way to login if you already have an account and it should provide a way to register with a new account.

![alt tag](https://github.com/aeria-io/DonkiesRestAPI/blob/master/readme_assets/CreateAccount-2.png)

# Register Debit Account
After the user logs in or creates an account, the modal should slide to the left and present the user with this form. This form takes care of registering a debit account (bank account) with the user. In order for a user to access the dashboard, he must have a debit account registered. If a user has signed up but hasn't registered an account, this should be the form he sees upon loggin in again.

![alt tag](https://github.com/aeria-io/DonkiesRestAPI/blob/master/readme_assets/LinkBank-3.png)

# Dashboard
Here is where all the transaction data will be viewed and summarized.

![alt tag](https://github.com/aeria-io/DonkiesRestAPI/blob/master/readme_assets/DashBoard-5.png)


## Phase 2:

# Register Loan Account
This will be fore phase 2 of the project. No need to work on this part now.

![alt tag](https://github.com/aeria-io/DonkiesRestAPI/blob/master/readme_assets/LinkLender-4.png)



