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

* We do not control accounts when we still have member. When user's member has multiple accounts, after deleting one account, member still available. This is confusing situation. When user creates account in Atrium, actually it creates member. 
And if member has multiple accounts - user actually will create multiple accounts.

But in Donkies user operates with accounts (not members). This is rare situation, so to avoid confusions, proposal:

If user wants to delete account and account's member has other account (For example 2 accounts in Chase bank under single credentials), give user the message that both accounts will be deleted and if it confirms, delete both accounts. (Proposal not implemented yet.)
* Test not implemented yet.



## Transaction

* "delete" method on Model should not delete object, instead set is_active=False
* TestTransaction.test_delete01

* "delete" method on QuerySet should not delete objects, instead set is_active=False
* TestTransaction.test_delete02


# TESTS FOR TRANSFERS


## TransferPrepare

* Test "process_roundups" manager's method. The number of TransferPrepare rows after processing should be equal to number of debit accounts.
* TransferPrepare.test01

* Test "process_roundups" manager's method. The sum of roundup of not processed transactions should be equal to sum that inserted TransferPrepare. All transactions after that should be marked as processed.
* TransferPrepare.test02



## TransferDonkies

* Test "process_prepare" manager's method. If user does not set funding source debit account, do not process. TransferDonkies should have zero rows.
* TestDonkies.test01

* Test "process_prepare" manager's method. Each user should get only one aggregated row for TransferDonkies model.
* TestDonkies.test02

* Test "process_prepare" manager's method. The total amount for each user in all  TransferPrepare should be equal the amount in TransferDonkies row.
* TestDonkies.test03

* Test "process_prepare" manager's method. After moving funds from TransferPrepare to TransferDonkies all items in TransferPrepare should be set to is_processed=True
* TestDonkies.test04

* Test "move_failed" manager's method. After moving TransferDonkies item to TransferDonkiesFailed, all fields should be equal, TransferDonkies should be removed.
* TestDonkies.test05



## TransferDonkies with calling Dwolla API and other Dwolla API items.

* Test "create_dwolla_customer" bank manager's method. Should set dwolla_id to Customer.
* TestDonkiesDwolla.test01

* Test "initiate_dwolla_customer" bank manager's method. Should set dwolla_type, status, created_at to Customer.
* TestDonkiesDwolla.test02

* Test "create_customer" DwollaApi method. Try to create the same customer twice. Instead of getting error second time, should get customer.
* TestDonkiesDwolla.test03

* Test "initiate_dwolla_transfer" manager's method. After TransferDonkies is initiated, should get everything that described in TransferDonkies model.
* TestDonkiesDwolla.test04

* Test "update_dwolla_transfer" manager's method. Test successful transfer.
* TestDonkiesDwolla.test05

* Test "update_dwolla_transfer" manager's method. Test FAILED R01 status. In testing environment set name = "R01" to funding source and it will respond with that error.
* TestDonkiesDwolla.test06

!!! Init transfer can fail with not sufficient funds.
!!! Process this case. Delay for next init.