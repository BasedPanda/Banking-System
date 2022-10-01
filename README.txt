Welcome to Banking System. 

Here, I will be taking you through how to run the program and what it can do.



HOW TO RUN THE PROGRAM

>The user doesn't have to take any additional steps before running the program. Once you run the program, it will directly check if you have the database already in your server. If not, it will directly use the 'SETUP.txt" file to create the database and all the tables. The 'DATE.txt' and 'MYSQL_DETAILS.txt' files will be created if not found in your folder.





WHAT THE PROGRAM DOES

>Creates new users: Creates new user when entered basic information.

>Creates new accounts: Creates Savings Account, Current Account or Fixed Deposit depending on the user's choice for an existing user.

>Loans: Issues loans to existing users, allows the user to pay EMI and also allows the user to pay the fine for a missed EMI.

>Deposit/Withdraw: Allows user to deposit/withdraw money from Savings and Current Account.

>Show Customer Details: Shows personal details, account details, loan details, transaction details or fine details for a selected user. Transactions include deposits/withdrawal,
 			loan EMI payments, loan issuances, fine payments, etc.

>Change Customer Details: Allows the customer to change their name, phone number and monthly income.

>Forgot CustomerID: Retrieves the customer ID if provided with the correct pairing of name and phone number.

>Forgot Account Details: Retrieves the account number(s) if provided with the Customer ID and the type of account

>Change month: Analogous to change in time. By selecting this option, the date progresses to the next month. EMI payment records, Savings Interest and FD interest are updated simultaneously.
 	       FDs that have completed time period have their amounts transferred to a Savings account of the same customer. Also, if the payment of last month's EMI has not been made,
	       the fine is entered

>Exit: Allows you to terminate the program so that the next time, you can continue from where you left off.

>Restart database: Deletes all data and tables in the database and drops the database. The next time you use this program, you have to answer 'y' when asked if you are running the program 
 for the first time on this device.






