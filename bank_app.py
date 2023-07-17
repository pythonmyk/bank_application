import argparse
import csv
from datetime import datetime
import random
import string
import sqlite3


class BankAccount:
    def __init__(self, account_type="Debit", credit_limit=0):
        self.account_type = account_type
        self.credit_limit = credit_limit
        self.currency = "USD"  # Default currency
        self.currency_rates = {"USD": 1.0}  # Currency exchange rates
        self.conn = sqlite3.connect("bank.db")
        self.cursor = self.conn.cursor()

        self._create_table()

    def _create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions
                            (transaction_reference TEXT PRIMARY KEY, date TEXT, description TEXT, amount REAL, currency TEXT)''')
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

    def generate_transaction_reference(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(16))

    def is_valid_transaction_reference(self, transaction_reference):
        # Check if the transaction_reference is exactly 16 characters long and contains only letters and digits.
        return len(transaction_reference) == 16 and transaction_reference.isalnum()

    def compute_balance(self, date=None):
        query = "SELECT SUM(amount) FROM transactions"
        params = ()
        if date:
            query += " WHERE date <= ?"
            params = (date,)

        self.cursor.execute(query, params)
        result = self.cursor.fetchone()[0]

        return result if result else 0.0

    def get_balance_at_date(self, date):
        query = "SELECT SUM(amount) FROM transactions WHERE date <= ?"
        self.cursor.execute(query, (date,))
        result = self.cursor.fetchone()[0]
        return result if result else 0.0

    def get_transactions_for_period(self, start_date, end_date):
        query = "SELECT * FROM transactions WHERE date BETWEEN ? AND ?"
        self.cursor.execute(query, (start_date, end_date))
        return self.cursor.fetchall()

    def print_transactions(self):
        transactions = self.get_transactions()
        print("Transactions:")
        for transaction in transactions:
            print(transaction)

    def import_transactions(self, file_path, currency_rates_file):
        current_balance = self.compute_balance()
        initial_balance = current_balance
        import_successful = True

        # Load currency rates from the specified file
        currency_rates = import_currency_rates(currency_rates_file)
        self.set_currency(self.currency, currency_rates)  # Update the bank account with the currency rates

        # Format the current balance before import to two decimal places with currency symbol
        formatted_current_balance = "{:.2f} {}".format(current_balance, self.currency)
        print(f"Current balance before import: {formatted_current_balance}")

        valid_transactions = []

        with open(file_path, "r") as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header row
            for row in reader:
                if len(row) != 5:
                    print(f"Skipping invalid row: {row}")
                    continue

                transaction_reference, date_str, description, amount_str, currency = row
                try:
                    amount = float(amount_str)
                except (ValueError, TypeError):
                    print(f"Skipping invalid row: {row}")
                    continue

                if not self.is_valid_transaction_reference(transaction_reference):
                    print(f"Invalid transaction reference: {transaction_reference}. Skipping row: {row}")
                    continue

                if self._is_duplicate_transaction(transaction_reference):
                    print(f"Duplicate transaction reference: {transaction_reference}. Skipping row: {row}")
                    continue

                # Convert the transaction amount to the account currency
                converted_amount = self.convert_currency(amount, currency, self.currency, date_str)

                if converted_amount is None:
                    print(f"Missing currency rates for {currency} on {date_str}. Unable to find a rate in the past.")
                    print(
                        f"Failed to convert amount for currency {currency} on {date_str}. Skipping the current import.")
                    import_successful = False
                    break

                # Convert the currency symbol to the destination currency after conversion
                converted_currency = self.currency if currency == self.currency else self.currency
                current_balance = current_balance + converted_amount

                if self.account_type == "Debit" and current_balance < 0:
                    print(f"Invalid amount for Debit account: {amount}. Skipping the current import.")
                    import_successful = False
                    break

                if self.account_type == "Credit" and current_balance < -self.credit_limit:
                    print(f"Transaction exceeds credit limit. Skipping the current import.")
                    import_successful = False
                    break

                # The transaction is valid; add it to the list to be inserted into the database
                valid_transactions.append(
                    (transaction_reference, date_str, description, converted_amount, converted_currency))

            if import_successful:
                # Insert all the valid transactions into the database at once
                self.cursor.executemany(
                    "INSERT INTO transactions (transaction_reference, date, description, amount, currency) VALUES (?, ?, ?, ?, ?)",
                    valid_transactions)

                self.conn.commit()  # Commit the transactions to the database if import is successful
                print("Import successful.")
            else:
                print(f"Import rolled back. Current balance remains: {initial_balance}.")

        print(f"Current balance: {current_balance:.2f} {self.currency}")
        self.print_transactions()

    def _is_duplicate_transaction(self, transaction_reference):
        query = "SELECT COUNT(*) FROM transactions WHERE transaction_reference = ?"
        self.cursor.execute(query, (transaction_reference,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def get_transactions(self, start_date=None, end_date=None):
        query = "SELECT * FROM transactions"
        params = []
        if start_date and end_date:
            query += " WHERE date BETWEEN ? AND ?"
            params = (start_date, end_date)
        elif start_date:
            query += " WHERE date >= ?"
            params = (start_date,)
        elif end_date:
            query += " WHERE date <= ?"
            params = (end_date,)

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def set_account_type(self, account_type, credit_limit=0):
        self.account_type = account_type
        self.credit_limit = credit_limit

    def set_currency(self, currency, rates):
        self.currency = currency
        self.currency_rates = rates

    def convert_currency(self, amount, from_currency, to_currency, date_str):
        if from_currency == to_currency:
            return amount

        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        key_from = (from_currency, date)
        key_to = (to_currency, date)

        if key_from not in self.currency_rates or key_to not in self.currency_rates:
            print(f"Missing currency rates for {from_currency} to {to_currency} on {date}.")
            return None

        rate = self.currency_rates[key_to] / self.currency_rates[key_from]
        return amount * rate

    def save_data(self):
        self.cursor.execute("DROP TABLE IF EXISTS transactions")
        self._create_table()

        transactions = self.get_transactions()
        for transaction in transactions:
            converted_amount = self.convert_currency(transaction[3], transaction[4], self.currency)
            self.cursor.execute("INSERT INTO transactions (transaction_reference, date, description, amount, currency) VALUES (?, ?, ?, ?, ?)",
                                (transaction[0], transaction[1], transaction[2], converted_amount, self.currency))

        self.conn.commit()

    def delete_all_transactions(self):
        query = "DELETE FROM transactions"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()


def import_currency_rates(file_path):
    currency_rates = {}
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            if len(row) != 4:
                print(f"Skipping invalid row: {row}")
                continue

            currency, rate_str, base_currency, date_str = row
            try:
                rate = float(rate_str)
            except (ValueError, TypeError):
                print(f"Skipping invalid row: {row}")
                continue

            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            key = (currency, date)

            if key in currency_rates:
                currency_rates[key] = rate / currency_rates[key]
            else:
                currency_rates[key] = rate

    return currency_rates


def parse_arguments():
    parser = argparse.ArgumentParser(description="Bank Account Application")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Import command
    parser_import = subparsers.add_parser("import", help="Import transactions from a CSV file")
    parser_import.add_argument("file_path", type=str, help="Path to the CSV file containing transactions")
    parser_import.add_argument("currency_rates_file", type=str,
                               help="Path to the CSV file containing currency exchange rates")

    # Balance command
    parser_balance = subparsers.add_parser("balance", help="Query account balance at a specific date")
    parser_balance.add_argument("date", type=str, help="Date in YYYY-MM-DD format")

    # Transactions command
    parser_transactions = subparsers.add_parser("transactions", help="Query transactions for a specific period")
    parser_transactions.add_argument("start_date", type=str, help="Start date in YYYY-MM-DD format")
    parser_transactions.add_argument("end_date", type=str, help="End date in YYYY-MM-DD format")

    # Set account type command
    parser_set_account_type = subparsers.add_parser("set_account_type", help="Set the account type and credit limit")
    parser_set_account_type.add_argument("account_type", type=str, choices=["Debit", "Credit"],
                                         help="Account type (Debit or Credit)")
    parser_set_account_type.add_argument("--credit_limit", type=float, default=0,
                                         help="Credit limit for the Credit account")

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.command == "set_account_type":
        bank_account = BankAccount(account_type=args.account_type, credit_limit=args.credit_limit)
    else:
        bank_account = BankAccount()  # Default account type is Debit with credit_limit=0

    if args.command == "import":
        bank_account.import_transactions(args.file_path, args.currency_rates_file)
    elif args.command == "balance":
        date = datetime.strptime(args.date, "%Y-%m-%d").date()
        balance = bank_account.compute_balance(date)
        print(f"Account balance on {args.date}: {balance:.2f} {bank_account.currency}")
    elif args.command == "transactions":
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
        transactions = bank_account.get_transactions(start_date, end_date)
        print(f"Transactions for the period {args.start_date} to {args.end_date}:")
        for transaction in transactions:
            print(transaction)
    elif args.command == "set_account_type":
        bank_account.set_account_type(args.account_type, args.credit_limit)
        print("Account type and credit limit updated successfully.")

    bank_account.close_connection()


if __name__ == "__main__":
    main()
