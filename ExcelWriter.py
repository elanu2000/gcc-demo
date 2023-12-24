from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class ExcelWriter:
    def __init__(self, target_match, SPREADSHEET_ID = ''):
        self.target_match = target_match
        self.SPREADSHEET_ID = '1wseMtOZXNLL_fWxrTHhqApJluSYIPy8I9WVrSfMXzb0'
        self.create_service()
    
    def create_service(self):
        SERVICE_ACCOUNT_FILE = '/Users/elanu/Documents/GCC/gcyr-408819-83b15ce5b8eb.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)

        # Function to find a row based on a condition
    def find_row(self, sheet_service, target_value, column):
        # Adjust range as necessary. Here it reads column B for all rows
        range_name = f'Foaie1!{column}1:{column}1000'
        result = sheet_service.spreadsheets().values().get(
            spreadsheetId=self.SPREADSHEET_ID, range=range_name).execute()
        values = result.get('values', [])

        for i, row in enumerate(values):
            if row and row[0] == target_value:
                return i + 1  # +1 because Sheets is 1-indexed, not 0-indexed
        return None
    
    # Function to update a specific cell
    def update_cell(self, sheet_service, row_number, value, column_index):
        cell_name = f'Foaie1!{chr(65 + column_index)}{row_number}'
        body = {'values': [[value]]}
        result = sheet_service.spreadsheets().values().update(
            spreadsheetId=self.SPREADSHEET_ID, range=cell_name,
            valueInputOption='USER_ENTERED', body=body).execute()
        return result

    def write_goals_corners_cards(self, goals, corners, adjusted_cards):
        # Your target values
        target_in_column_C = self.target_match
        value_to_write = goals * corners * adjusted_cards

        # Find the row
        row_number = self.find_row(self.service, target_in_column_C, 'C')
        if row_number:
            # Update the cell
            result = self.update_cell(self.service, row_number, value_to_write, 12)
            result = self.update_cell(self.service, row_number, goals, 9)
            result = self.update_cell(self.service, row_number, corners, 11)
            result = self.update_cell(self.service, row_number, adjusted_cards, 10)
            print(f"Updated cell: {result.get('updatedCells')} cells updated.")
        else:
            print("Target value not found in column C.")

    def search_next_empty_row(self):
        return self.find_row(self.service, '0', 'I')

    def write_predictions(self, predictions):
        empty_row = self.search_next_empty_row()
        print("empty_row: " + str(empty_row))
        result = self.update_cell(self.service, empty_row, self.target_match, 2)
        for index, prediction in enumerate(predictions):
            column = index + 3
            print(column, prediction)
            result = self.update_cell(self.service, empty_row, int(prediction), column)
            print(f"Updated cell: {result.get('updatedCells')} cells updated.")