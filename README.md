# Bank App

Write a bank application with python (preferably with `+3.10` version) that can accept incoming and outgoing money transactions.

## Requirements

* You can import a file of transactions into your bank application. Transaction at 
  minimum should consist of:
    * Date of the transaction
    * Description of transaction
    * Amount: positive amount is incoming transaction (money you receive) , negative is 
      outgoing transaction (money you spent on something)
* Imported data is computed to show balance of your account.
* Add an option to specify type of account for your bank app. It can be either Debit 
  (balance can't be negative) or Credit (balance can be negative up to specified amount)
* Should be possible to save imported data, so next time bank app is loaded, it will have 
  history of already imported data.
* When data is imported, it should print current balance of your account.
* You should be able to query your bank account to return balance at specific date or
  return transactions of specific period (e.g. we specify transactions date range and 
  we get all transactions for that range).
* There should be some basic tests that validate that app is working:
    * Import incoming and outgoing transactions. Get current balance of account.
    * Import transactions with different dates. Get balance of specific date (also can 
      write test when there are no transactions for wanted date).
    * Try to import transactions that would make a balance negative in Debit type of account.
    * Import transactions when it would make it negative balance in Credit type of Account (also when it would go over the credit limit as well).

### Bonus

Add multi currency support:

* Specify used currencies with their rates on specific dates (loaded by bank app).
* Transaction should now specify which currency it uses.
* Bank app uses one specific currency, where other currency rates are bases on that currency.
* When transactions are imported in bank app, amounts are converted to account currency.

### Extra Info

UI for bank APP does not matter, can even be simple prints.
App can work just like a simple program that accepts arguments and produces output and saves data somewhere.
Bank Account Application
========================

This Python script provides a simple Bank Account Application to manage transactions and account balance for a Debit or Credit account. The application allows you to import transactions from a CSV file, check the account balance at a specific date, query transactions for a specific period, and set the account type and credit limit.

Usage
-----

1. Setup

    -   Before running the application, ensure you have Python 3 installed on your system.

    -   Download or clone the repository from GitHub: [Bank Account Application](https://github.com/example-user/bank-account-application).

    -   Install the required dependencies using pip:

        `pip install sqlite3`

2. Commands and Arguments

    The Bank Account Application supports the following commands and their respective arguments:

    -   import

        Import transactions from a CSV file.

        arduinoCopy code

        `python3 bank_app.py import file_path currency_rates_file`

        -   `file_path`: The path to the CSV file containing transactions. Each row in the CSV file should contain the transaction reference, date, description, amount, and currency.
        -   `currency_rates_file`: The path to the CSV file containing currency exchange rates. Each row should contain the currency code, exchange rate, base currency, and date.

        Restrictions:

        -   The `file_path` and `currency_rates_file` arguments are required.
        -   The CSV files should have a header row, and the columns must be in the correct order.
    -   balance

        Query the account balance at a specific date.

        `python3 bank_app.py balance date`

        -   `date`: The date in YYYY-MM-DD format for which you want to check the account balance.

        Restrictions:

        -   The `date` argument is required and should be in the format "YYYY-MM-DD".
    -   transactions

        Query transactions for a specific period.

        `python3 bank_app.py transactions start_date end_date`

        -   `start_date`: The start date in YYYY-MM-DD format.
        -   `end_date`: The end date in YYYY-MM-DD format.

        Restrictions:

        -   Both `start_date` and `end_date` arguments are required.
        -   Dates should be in the format "YYYY-MM-DD".
        -   Transactions between the start and end dates (inclusive) will be displayed.
    -   set_account_type

        Set the account type and credit limit.

        `python3 bank_app.py set_account_type account_type [--credit_limit]`

        - `account_type`: The account type (Debit or Credit).
        - `--credit_limit`: (Optional) The credit limit for the Credit account. Only applicable for the "Credit" account type.

        - Restrictions:

        - The `account_type` argument is required and should be one of "Debit" or "Credit".
        - If the `account_type` is "Credit", the `--credit_limit` argument is optional, but if provided, it must be a valid floating-point number.
        
3. Running the Application

   To execute the Bank Account Application, open a terminal or command prompt, navigate to the directory where `bank_app.py` is located, and run the desired commands as shown in the usage examples above.

   For example, to import transactions from a CSV file named `transactions.csv` and a currency exchange rates file named `currency_rates.csv`, you would run the following command:

   arduinoCopy code

   `python3 bank_app.py import transactions.csv currency_rates.csv`

   Make sure to replace `transactions.csv` and `currency_rates.csv` with the actual file paths.

### Note

-   The application will create a SQLite database named "bank.db" in the same directory as the script to store transactions.

-   Ensure that your CSV files are formatted correctly and contain valid data for the application to work properly.

-   You can find demo data examples in the project files