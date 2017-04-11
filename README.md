### Difference between Stripe and Dwolla.

When user added Item via Plaid Link - we can fetch all accounts that available for institution. In Stripe we already can get stripe token for any account and assign account as funding source for transfers. All institutions should have "auth" product. Not "auth" institutions can not be integrated to Stripe. In case with Dwolla and micro-deposits for not "auth" institutions it is not possible to get account_number and routing_number by Plaid API.

In Dwolla we need to create funding source first - via IAV or micro-deposits.
To create funding source - we also need to create customer in Dwolla (user's profile should be completed). With Stripe user doesn't need to complete profile.

### Share change between all debt accounts.

1) The share is in percentage.
2) First account will get 100% by default.
3) All next accounts will get 0% by default.
4) User is able to assign any value in dashboard.
5) The sum of share of all debt accounts should be equal 100%.


### Transfer flow.
Instructions in TransferPrepare and TransferDonkies model.

### User flow

1) User sign up. After sign up user will get email where it should confirm registration. After confirmation user.is_confirmed = True. If user sign up by facebook, it confirmed automatically.

2) User need to add bank accounts (items). As soon as items are created via Plaid Link, all accounts and transactions for these items will be available. Accounts are available immediately. Transactions after some time. Transactions are updated by webhooks.

3) User adds debt accounts manually. We have internal Items for consistency, but these items (for debt accounts) are not connected to Plaid and we can't fetch transactions. "plaid_id" = None

4) In settings User set minimum_transfer_amount (By default $5 and can be changed in settings) and is_auto_transfer.

5) Roundup is transfered to Donkies as soon as user's collected roundup is more than settings.TRANSFER_TO_DONKIES_MIN_AMOUNT

6) On 15th of current month if user set auto transfer and total amount of previous month more than minimum transfer amount (in user settings), send money to user (TransferUser model).

7) Send money to user's debt accounts from TransferUser (TransferDebt) model. (Currently manually by cheques)
