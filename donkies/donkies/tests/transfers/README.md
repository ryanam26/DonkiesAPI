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

* Accounts are not deleted from user interface. User set them active/not active.


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


## Transaction

* "delete" method on Model should not delete object, instead set is_active=False
* TestTransaction.test_delete01

* "delete" method on QuerySet should not delete objects, instead set is_active=False
* TestTransaction.test_delete02
