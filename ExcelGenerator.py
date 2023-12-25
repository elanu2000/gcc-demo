from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class ExcelGenerator:
    def __init__(self, room_id, players_name):
        self.create_service()
        self.create_new_spreadsheet(room_id, players_name)

    def create_service(self):
        SERVICE_ACCOUNT_FILE = 'gcyr-408819-83b15ce5b8eb.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)

    def create_new_spreadsheet(self, title, players_name):
        spreadsheet_body = {
            'properties': {
                'title': title
            }
        }
        request = self.service.spreadsheets().create(body=spreadsheet_body)
        response = request.execute()

        # The response contains the new spreadsheet ID
        spreadsheet_id = response.get('spreadsheetId')

        self.set_public_permission(spreadsheet_id)

        self.populate_new_spreadsheet(spreadsheet_id, players_name)

        return spreadsheet_id
    
    def set_public_permission(self, spreadsheet_id):
        permission = {
            'type': 'anyone',
            'role': 'writer'  # Change to 'writer' if you want public edit access
        }
        self.drive_service.permissions().create(fileId=spreadsheet_id, body=permission).execute()

    def update_cell(self, row_number, value, column_index):
        cell_name = f'Sheet1!{chr(65 + column_index)}{row_number}'
        body = {'values': [[value]]}
        result = self.service.spreadsheets().values().update(
            spreadsheetId=self.SPREADSHEET_ID, range=cell_name,
            valueInputOption='USER_ENTERED', body=body).execute()
        return result

    def populate_new_spreadsheet(self, spreadsheet_id, players_name):
        self.SPREADSHEET_ID = spreadsheet_id
        print(spreadsheet_id)
        for index, player_name in enumerate(players_name):
            self.update_cell(2, player_name, 3 + index)
        self.update_cell(3, "Traded Price", 4 + len(players_name))
        self.update_cell(3, "Goals", 5 + len(players_name))
        self.update_cell(3, "Cards", 6 + len(players_name))
        self.update_cell(3, "Corners", 7 + len(players_name))
        self.update_cell(3, "Settled Price", 8 + len(players_name))

        requests = []
        column = 4 + len(players_name)
        player_columns = [chr(ord('D') + i) for i in range(len(players_name))]
        # Building the request for each row
        for i in range(12, 1000 + 1):
            player_cells = ','.join([f'{col}{i}' for col in player_columns])
            # formula = f'=IF(D{i}*E{i}*F{i}*G{i}, MEDIAN(D{i}, E{i}, F{i}, G{i}), 0)'
            formula = f'=IF(COUNTA({player_cells}) = 0, 0, MEDIAN(FILTER({{{player_cells}}}, {{{player_cells}}} <> "")))'

            requests.append({
                'updateCells': {
                    'range': {
                        # 'sheetId': 0,  # Update with your actual sheet ID if not the first sheet
                        'startRowIndex': i - 1,
                        'endRowIndex': i,
                        'startColumnIndex': column,
                        'endColumnIndex': column + 1
                    },
                    'rows': [{
                        'values': [{'userEnteredValue': {'formulaValue': formula}}]
                    }],
                    'fields': 'userEnteredValue'
                }
            })

        # Send batch update
        body = {
            'requests': requests
        }
        response = self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body).execute()