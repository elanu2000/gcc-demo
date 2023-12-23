import requests, json

class MatchStatistics:
    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team
        if home_team in self.team_dict:
            self.querystring_match = {"team_id": self.team_dict[home_team]}
        elif away_team in self.team_dict:
            self.querystring_match = {"team_id": self.team_dict[away_team]}
        else:
            self.querystring_match = {}

    with open("team_dict.json", "r") as file:
        team_dict = json.load(file)

    url_endpoint = "https://sofascores.p.rapidapi.com/v1"
    url_match_suffix = "/teams/near-events"
    url_statistics_suffix = "/events/statistics"
    url_incidents_suffix = "/events/incidents"
    headers = {
        "X-RapidAPI-Key": "4262a4297emshdf95e4a21863915p1ec56bjsnbd1c62f6586a",
        "X-RapidAPI-Host": "sofascores.p.rapidapi.com"
    }

    total_goals = 0
    total_corners = 0
    total_yellow_cards = 0
    total_red_cards = 0

    def get_event_id(self):
        if len(self.querystring_match) == 0:
            Exception("No team is registered in team_dict")
        response = requests.get(self.url_endpoint + self.url_match_suffix, headers=self.headers, params=self.querystring_match)
        response = response.json()
        event_json = response['data']['previousEvent']
        event_id = int(event_json['id'])
        self.querystring_statistics = {"event_id": str(event_id)}
        return str(event_id)

    def get_start_timestamp(self, event_id):
        response = requests.get(self.url_endpoint + self.url_match_suffix, headers=self.headers, params=self.querystring_match)
        response = response.json()
        event_json = response['data']['previousEvent']
        start_timestamp = int(event_json['startTimestamp'])
        return start_timestamp
    
    def is_match_finished(self):
        response = requests.get(self.url_endpoint + self.url_match_suffix, headers=self.headers, params=self.querystring_match)
        response = response.json()
        event_json = response['data']['previousEvent']
        if "status" in event_json and event_json["status"]["type"] == "finished":
            return True
        return False 

    def get_goals(self):
        if len(self.querystring_match) == 0:
            Exception("No team is registered in team_dict")
        response = requests.get(self.url_endpoint + self.url_match_suffix, headers=self.headers, params=self.querystring_match)
        response = response.json()
        event_json = response['data']['previousEvent']
        self.total_goals = int(event_json['homeScore']['current'] + event_json['awayScore']['current'])
        print("Total goals: " + str(self.total_goals))
    
    def get_adjusted_cards(self):
        response = requests.get(self.url_endpoint + self.url_incidents_suffix, headers=self.headers, params=self.querystring_statistics)
        response = response.json()
        self.total_yellow_cards = 0
        self.total_red_cards = 0
        if "data" in response:
            for incident in response["data"]:
                if incident["incidentType"] == "card":
                    if incident["incidentClass"] == "yellow":
                        self.total_yellow_cards += 1
                    else:
                        self.total_red_cards += 1
        print("Total yellow cards: " + str(self.total_yellow_cards))
        print("Total red cards: " + str(self.total_red_cards))
        self.total_adjusted_cards = self.total_yellow_cards + 2 * self.total_red_cards


    def get_total_corners(self):
        response = requests.get(self.url_endpoint + self.url_statistics_suffix, headers=self.headers, params=self.querystring_statistics)
        response = response.json()

        # Extracting data from the response
        for group in response['data'][0]['groups']:
            if group['groupName'] == 'TVData':
                for stat in group['statisticsItems']:
                    if stat['name'] == 'Corner kicks':
                        self.total_corners = int(stat['home']) + int(stat['away'])
        print("Total corners: " + str(self.total_corners))
        
        
    def get_total_score(self):
        return self.total_goals * self.total_corners * (self.total_yellow_cards + 2 * self.total_red_cards)
