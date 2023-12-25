from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import string, time

class ExcelWriter:
    def __init__(self, SPREADSHEET_ID):
        self.create_service()
        # self.SPREADSHEET_ID = '1wseMtOZXNLL_fWxrTHhqApJluSYIPy8I9WVrSfMXzb0'
        self.SPREADSHEET_ID = SPREADSHEET_ID
    
    def create_service(self):
        SERVICE_ACCOUNT_FILE = 'gcyr-408819-83b15ce5b8eb.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)

        # Function to find a row based on a condition
    def find_row(self, target_value, column, starting_row = 1):
        # Adjust range as necessary. Here it reads column B for all rows
        range_name = f'Sheet1!{column}1:{column}1000'
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.SPREADSHEET_ID, range=range_name).execute()
        values = result.get('values', [])

        for i, row in enumerate(values):
            if row and row[0] == target_value and i >= starting_row - 1:
                return i + 1  # +1 because Sheets is 1-indexed, not 0-indexed
        return None
    
    def find_column(self, target_value, row_number):
        # Adjust range as necessary. Here it reads the entire row.
        range_name = f'Sheet1!{row_number}:{row_number}'

        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.SPREADSHEET_ID, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            return None  # Row is empty or doesn't exist

        # Assuming values[0] contains the first row in the range
        for i, value in enumerate(values[0]):
            if value.strip() == target_value:
                return i

        Exception(target_value + " not found in spreadsheet!")

    
    # Function to update a specific cell
    def update_cell(self, row_number, value, column_index):
        cell_name = f'Sheet1!{chr(65 + column_index)}{row_number}'
        body = {'values': [[value]]}
        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.SPREADSHEET_ID, range=cell_name,
            valueInputOption='USER_ENTERED', body=body).execute()
        return result
    
    def get_cell_value(self, row, column):
        # Convert the column index to a letter (A, B, C, ...)
        column_letter = string.ascii_uppercase[column]

        # Construct the cell range in A1 notation
        cell_range = f'Sheet1!{column_letter}{row}'

        # Use the Sheets API to get the cell's value
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.SPREADSHEET_ID,
            range=cell_range).execute()

        # Extract the value
        values = result.get('values', [])
        if not values or not values[0]:
            return None
        return values[0][0]

    def write_goals_corners_cards(self, target_match, goals, corners, adjusted_cards):
        # Your target values
        target_in_column_C = target_match
        value_to_write = goals * corners * adjusted_cards

        # Find the row
        row_number = self.find_row(target_in_column_C, 'C')
        if row_number:
            # Update the cell
            result = self.update_cell(row_number, value_to_write, self.find_column("Settled Price", 3))
            result = self.update_cell(row_number, goals, self.find_column("Goals", 3))
            result = self.update_cell(row_number, corners, self.find_column("Corners", 3))
            result = self.update_cell(row_number, adjusted_cards, self.find_column("Cards", 3))
            print(f"Updated cell: {result.get('updatedCells')} cells updated.")
        else:
            print("Target value not found in column C.")

    def search_next_empty_row(self):
        column = self.find_column('Traded Price', 3)
        print(column)
        row_number = 0
        while True:
            row_number = self.find_row('0', string.ascii_uppercase[column], row_number + 1)
            print(row_number)
            is_row_empty = True
            for column_index in range(2, column):
                if self.get_cell_value(row_number, column_index) is not None:
                    is_row_empty = False
            if is_row_empty:
                return row_number
            time.sleep(0.2)

    def write_predictions(self, players_input, target_match):
        empty_row = self.search_next_empty_row()
        print("empty_row: " + str(empty_row))
        print(players_input)
        result = self.update_cell(empty_row, target_match, 2)
        for player_dict in players_input:
            target = player_dict["name"]
            column = self.find_column(target, 2)
            prediction = player_dict["prediction"]
            print(column, prediction)
            result = self.update_cell( empty_row, int(prediction), column)
            print(f"Updated cell: {result.get('updatedCells')} cells updated.")