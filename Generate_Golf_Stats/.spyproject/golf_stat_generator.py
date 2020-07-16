import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

pp = lambda *msgs: pprint.PrettyPrinter.pprint(msgs)

def main():
    data = get_data()
    sorted_data = sorted(data, key=lambda x: x["DATE"], reverse=True)
    rounds = create_rounds_from_data(sorted_data)
#    fir_pct = calculate_fir_percentage(sorted_data)


def get_data():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
            r'C:\Users\thisi\Documents\Python Scripts\golf_stat_tracker'
            '\Golf Stats-40fdfecf8fde.json', scope)
    client = gspread.authorize(creds)
    
    sheet = client.open('FGPS Stats').worksheet("Data")
    
    golf_data = sheet.get_all_records()
    return golf_data


def create_rounds_from_data(data):
    """
    golf is played in either 9 or 18 hole format. Whether played in 9 or 18
    holes, it is still called a 'round'. This function takes in the data
    and separates it into rounds played.
    """
    if data == None:
        raise Exception("No data to create statisitics on")
    
    rounds = []
    start_of_round = 0
    end_of_round = 0
    d = 0
    
    while d < len(data):
        rnd = []
        cur_hole = data[d]["HOLE"]
        next_hole = data[d+1]["HOLE"]
        
        if cur_hole == 18:
            rnd = [data[start_of_round:end_of_round]]
            rounds.append(rnd)
            start_of_round = end_of_round + 1
        elif cur_hole == 9 and next_hole == 1:
            rnd = [data[start_of_round:end_of_round]]
            start_of_round = end_of_round + 1
            rounds.append(rnd)
        else:
            d+=1
            end_of_round = d
    
#    for d in range(len(data)):
#        rnd = []
#        if d != len(data):
#            if data[d]["HOLE"] == 9 and data[d+1]["HOLE"] = 1:
                

def calculate_fir_percentage(data, rounds=None):
    """
    calculates the fairways in regulation
    takes in all golf stat data, pulls out the fir data and returns the
    percent of FIR's based on total holes played. `rounds` variable is used
    to set a timeframe of how many rounds the fir average should be calculated
    on. If set to `None` then calculate using all FIRs
    """
    
    firs = 0
    total_holes = 0
    
    if rounds == None:
        fir_data = [i["FIR"] for i in data]
        firs = len([i for i in fir_data if i.upper() == "F"])
        total_holes = len([i for i in fir_data if i.upper() in ["X", "F"]])
    else:
        pass
            
    return firs / total_holes

if __name__ == "__main__":
    main()