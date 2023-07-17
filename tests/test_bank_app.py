import unittest

from bank_app import BankAccount


class TestBankAccount(unittest.TestCase):
    def setUp(self):
        self.bank_account = BankAccount('Debit', 0)
        self.transactions_file = "sample_transactions.csv"
        self.currency_rates_file = "sample_currency_rates.csv"

    def test_import_transactions_and_balance(self):
        self.bank_account.delete_all_transactions()
        self.bank_account.import_transactions(self.transactions_file, self.currency_rates_file)

        transactions = self.bank_account.get_transactions()
        for transaction in transactions:
            print(f"Transaction: {transaction}")

        expected_balance_usd = 0.0
        for transaction in transactions:
            amount = transaction[3]
            currency = transaction[4]
            date_str = transaction[1]
            converted_amount_usd = self.bank_account.convert_currency(amount, currency, "USD", date_str)
            print(f"Converted amount in USD: {converted_amount_usd}")
            expected_balance_usd += converted_amount_usd

        print(f"Expected balance in USD: {expected_balance_usd}")
        actual_balance_usd = self.bank_account.compute_balance()
        print(f"Actual balance in USD: {actual_balance_usd}")

        self.assertAlmostEqual(expected_balance_usd, actual_balance_usd, places=2)

    def test_import_transactions_and_balance_specific_date(self):
        self.bank_account.delete_all_transactions()
        # Import transactions and currency rates
        self.bank_account.import_transactions(self.transactions_file, self.currency_rates_file)

        # Get the balance for a specific date
        balance_date = "2023-07-03"
        balance_usd = self.bank_account.compute_balance(balance_date)

        # Manually calculate the expected balance for the specific date
        expected_balance_usd = 0.0
        transactions = self.bank_account.get_transactions()
        for transaction in transactions:
            date_str = transaction[1]
            if date_str <= balance_date:
                amount = transaction[3]
                currency = transaction[4]
                converted_amount_usd = self.bank_account.convert_currency(amount, currency, "USD", date_str)
                expected_balance_usd += converted_amount_usd

        print(f"Expected balance on {balance_date} in USD: {expected_balance_usd}")
        print(f"Actual balance on {balance_date} in USD: {balance_usd}")

        self.assertAlmostEqual(expected_balance_usd, balance_usd, places=2)

    def test_import_transactions_negative_balance(self):
        self.bank_account.delete_all_transactions()
        self.bank_account.set_account_type('Debit', 0)
        initial_balance = self.bank_account.compute_balance()

        self.transactions_file = "test_transactions_debit.csv"

        # Import the transactions
        self.bank_account.import_transactions(self.transactions_file, self.currency_rates_file)

        # Manually calculate the expected final balance based on the transactions
        transactions = self.bank_account.get_transactions()
        expected_final_balance = initial_balance
        for transaction in transactions:
            expected_final_balance += self.bank_account.convert_currency(transaction[3], transaction[4], "USD",
                                                                         transaction[1])

        # Check that the balance remains the same as the initial balance (no transactions added)
        final_balance = self.bank_account.compute_balance()
        self.assertAlmostEqual(expected_final_balance, final_balance, places=2)
        self.bank_account.print_transactions()

    def test_import_transactions_negative_balance_credit(self):
        self.transactions_file = "test_transactions_credit.csv"
        self.bank_account = BankAccount('Credit', 20000)
        self.bank_account.delete_all_transactions()
        initial_balance = self.bank_account.compute_balance()

        # Import the transactions
        self.bank_account.import_transactions(self.transactions_file, self.currency_rates_file)

        # Check that the balance remains the same as the initial balance (no transactions added)
        final_balance = self.bank_account.compute_balance()

        # Expected final balance after the transactions: -5000.0 (initial_balance + 2000 - 7000)
        self.assertAlmostEqual(initial_balance, final_balance + 5000, places=2)
        self.bank_account.print_transactions()

    def test_import_transactions_negative_balance_credit_over_limit(self):
        self.transactions_file = "test_transactions_credit_over_limit.csv"
        self.bank_account = BankAccount('Credit', 20000)
        self.bank_account.delete_all_transactions()
        initial_balance = self.bank_account.compute_balance()

        # Import the transactions
        self.bank_account.import_transactions(self.transactions_file, self.currency_rates_file)

        # Check that the balance remains the same as the initial balance (no transactions added)
        final_balance = self.bank_account.compute_balance()

        # Expected final balance after the transactions have to be equal to initial balance
        self.assertAlmostEqual(initial_balance, final_balance, places=2)
        self.bank_account.print_transactions()

    def tearDown(self):
        # Close the database connection after each test
        self.bank_account.close_connection()


if __name__ == '__main__':
    unittest.main()
