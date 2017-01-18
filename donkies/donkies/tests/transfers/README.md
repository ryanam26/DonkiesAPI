# REQUIREMENTS FOR MEMBERS, ACCOUNTS, TRANSACTIONS IN RESPECT TO TRANSFERS.
 
 We can not delete Members, Accounts and Transactions from database.
 Instead each of this models will have boolean flag is_active.

 is_active = False - means that object is deleted by user.

 Later Celery task can look at Members, Accounts, and Transactions and items that was not used in transfers can be really deleted (if needed). Or they can stay in system for history.



## Members

* "delete" method on Model should not delete object, instead set is_active=False
* TestMember.test_delete01

* "delete" method on QuerySet should not delete objects, instead set is_active=False
* TestMember.test_delete02 

* Manager's method "delete_member" should set all related Accounts and Transactions to is_active=False
* TestMember.test_delete03

* Calling .objects.filter() should only be used from Manager's methods.
* No test.

* Calling "delete" methods should only be used from from Manager's methods.
* No test.



## Account

* "delete" method on Model should not delete object, instead set is_active=False
* TestAccount.delete01

* "delete" method on QuerySet should not delete objects, instead set is_active=False
* TestAccount.delete02

* Manager's method "delete_account" should set all related Transactions to is_active=False
* TestAccount.test_delete03

* Calling .objects.filter() should only be used from Manager's methods.
* No test.

* Calling "delete" methods should only be used from from Manager's methods.
* No test.





## Transaction

* "delete" method on Model should not delete object, instead set is_active=False
* TestTransaction.test_delete01

* "delete" method on QuerySet should not delete objects, instead set is_active=False
* TestTransaction.test_delete02

* Calling .objects.filter() should only be used from Manager's methods.
* No test.