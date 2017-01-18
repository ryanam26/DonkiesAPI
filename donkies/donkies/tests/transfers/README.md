# REQUIREMENTS FOR MEMBERS, ACCOUNTS, TRANSACTIONS IN RESPECT TO TRANSFERS.
 
We can not delete Members, Accounts and Transactions from database.
Instead each of this models will have boolean flag is_active.

is_active = False - means that object is deleted by user.

For filtering objects use manager's method .objects.active()

Later Celery task can look at Members, Accounts, and Transactions and items that was not used in transfers can be really deleted (if needed). Or they can stay in system for history.

## Requirements for Account, Member, Transaction.

* Calling .objects.filter() and .objects.all() should only be used from Manager's methods. From all other places use .objects.active() then filter() if needed.

* Calling "delete" methods should only be used from from Manager's methods.

* To delete members use only Member.objects.delete_member(member_id)

* To delete accounts use only Account.objects.delete_account(account_id)


## Members

* "delete" method on Model should not delete object, instead set is_active=False
* TestMember.test_delete01

* "delete" method on QuerySet should not delete objects, instead set is_active=False
* TestMember.test_delete02 

* Manager's method "delete_member" should set all related Accounts and Transactions to is_active=False
* TestMember.test_delete03


## Account

* "delete" method on Model should not delete object, instead set is_active=False
* TestAccount.delete01

* "delete" method on QuerySet should not delete objects, instead set is_active=False
* TestAccount.delete02

* Manager's method "delete_account" should set all related Transactions to is_active=False
* TestAccount.test_delete03

* When user delete account, we look if account's member has only this account, it also should be deleted.
* TestAccount.test_delete04, TestAccount.test_delete05

* We do not control accounts when we still have member. When user's member has multiple accounts, after deleting one account, member still available. And deleted account will be available again by API. So, when accounts and transactions are updated, we should update only active accounts.
* Test not implemented yet.

* When user deletes account and then create it again, if member is still in Atrium,
this will be existing account. So, on creating account look if it exists and set is_active=True
* Test not implemented yet.




## Transaction

* "delete" method on Model should not delete object, instead set is_active=False
* TestTransaction.test_delete01

* "delete" method on QuerySet should not delete objects, instead set is_active=False
* TestTransaction.test_delete02

