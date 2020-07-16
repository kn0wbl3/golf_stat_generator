import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
sys.path.append("C:/Users/thisi/Documents/Python Scripts")
import pretty_print
from statistics import mean 

COURSES_INFO = {
    "Pleasantville CC": {
        "slope": 119,
        "rating": 62.4,
    },
    "Van Cortlandt": {
        "slope": 119,
        "rating": 68.5
    },
    "New York CC": {
        "slope": 125,
        "rating": 67.7
    },
    "The Captains Golf Course": {
        "slope": 130,
        "rating": 69.4
    }
}

SLOPE_DIVISOR = 113

def main():
    """
    get data from google sheet
    sort it based on most recent date
    turn the data into rounds, can be 9 or 18 holes
    calc stats
        -FIR
        -GIR
        -AVG Putts
        -AVG Score
        -Handicap
    """
    stats = {}
    
    data = get_data()
    if not data:
        raise Exception("No data to parse")
    sorted_data = sorted(data, key=lambda x: x["DATE"], reverse=True)
    rounds = create_rounds_from_data(sorted_data)
    
    #all time
    all_time_fir_pct = calculate_percentage(rounds, "FIR", "F")
    all_time_gir_pct = calculate_percentage(rounds, "GIR", "G")
    all_time_putts_avg_nine = calculate_average(rounds, "PUTTS")["nine"]
    all_time_putts_avg_eighteen = calculate_average(rounds, "PUTTS")["eighteen"]
    all_time_score_avg_nine = calculate_average(rounds, "SCORE")["nine"]
    all_time_score_avg_eighteen = calculate_average(rounds, "SCORE")["eighteen"]
    handicap = calculate_handicap(rounds)
    
    #past 3 rounds
    three_fir_pct = calculate_percentage(rounds, "FIR", "F", rounds_to_calc=3)
    three_gir_pct = calculate_percentage(rounds, "GIR", "G", rounds_to_calc=3)
    three_putts_avg_nine = calculate_average(rounds, "PUTTS", rounds_to_calc=3)["nine"]
    three_putts_avg_eighteen = calculate_average(rounds, "PUTTS", rounds_to_calc=3)["eighteen"]
    three_score_avg_nine = calculate_average(rounds, "SCORE", rounds_to_calc=3)["nine"]
    three_score_avg_eighteen = calculate_average(rounds, "SCORE", rounds_to_calc=3)["eighteen"]
    
    #par 3's
    
    #par 4's
    
    #par 5's
    
    stats = {
        "all_time_fir_pct": all_time_fir_pct,
        "all_time_gir_pct": all_time_gir_pct,
        "all_time_putts_avg_nine": all_time_putts_avg_nine,
        "all_time_putts_avg_eighteen": all_time_putts_avg_eighteen,
        "all_time_score_avg_nine": all_time_score_avg_nine,
        "all_time_score_avg_eighteen": all_time_score_avg_eighteen,
        "handicap": handicap,
        "three_fir_pct": three_fir_pct,
        "three_gir_pct": three_gir_pct,
        "three_putts_avg_nine": three_putts_avg_nine,
        "three_putts_avg_eighteen": three_putts_avg_eighteen,
        "three_score_avg_nine": three_score_avg_nine,
        "three_score_avg_eighteen": three_score_avg_eighteen,
    }
    
    pstop(stats)

############################## FUNCTIONS IN MAIN ##############################

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
    
    rounds = []
    start_of_round = 0
    end_of_round = 1
    d = 0
    
    while d < len(data)-1:
        rnd = {}
        cur_hole = data[d]["HOLE"]
        next_hole = data[d+1]["HOLE"]
        
        if cur_hole == 18:
            rnd["data"] = data[start_of_round:end_of_round]
            rnd["is_nine"] = False
            rounds.append(rnd)
            start_of_round = end_of_round
        elif cur_hole == 9 and next_hole == 1:
            rnd["data"] = data[start_of_round:end_of_round]
            rnd["is_nine"] = True
            rounds.append(rnd)
            start_of_round = end_of_round
        elif d+1 == len(data)-1:
            rnd["data"] = data[start_of_round:]
            rnd["is_nine"] = (len(data) - start_of_round) == 9
            rounds.append(rnd)
        d+=1
        end_of_round = d+1
    return rounds


def calculate_percentage(
        data_universe, 
        data_key, 
        text, 
        rounds_to_calc=None,
        pars_to_calc=None
):
    """
    takes in all golf stat data, pulls out the `data_key` data and 
    returns the percent of `data_key` based on total holes played. 
    `rounds_to_calc` variable is used to set a timeframe of how many 
    rounds the `data_key` percentage should be calculated on. 
    If set to `None` then calculate using all FIRs
    
    data_universe: all rounds, dict
    data_key: key to be found in data_universe, string
    text: criteria to confirm based on data_universe[data_key], string
    rounds_to_calc: how many rounds to calculate, int
    pars_to_calc: which pars we want to focus on (3;s, 4's 5's)
    """
    data = []
    
    if rounds_to_calc == None:
        golf_rounds = data_universe
    else:
        golf_rounds = data_universe[:rounds_to_calc]
    
    # if pars_to_calc == None:
        
    
    for golf_round in golf_rounds:
        data += [i[data_key] for i in golf_round["data"]]
    stat = len([i for i in data if i.upper() == text])
    total_holes = len([i for i in data if i.upper() in ["X", text]])
    
    return round(stat / total_holes, 2)


def calculate_average(data_universe, data_key, rounds_to_calc=None):
    """
    calculates the mean putts made per round. putts count as a stroke
    on the green only. if on the fringe but hitting with a putter, it 
    doesn't count toward this stat. returns for nine and eighteen holes
    """
    summed_data = {
        "nine": [],
        "eighteen": []
    }
    
    average_data = {
        "nine": [],
        "eighteen": []
    }
    
    if rounds_to_calc == None:
        golf_rounds = data_universe
    else:
        golf_rounds = data_universe[:rounds_to_calc]
    
    for golf_round in golf_rounds:
        if golf_round["is_nine"]:
            summed_data["nine"].append(
                sum([i[data_key] for i in golf_round["data"]])
            )
        else:
            summed_data["eighteen"].append(
                sum([i[data_key] for i in golf_round["data"]])
            )
    
    average_data["nine"] = round(
        mean(summed_data["nine"]),
        2
    )if summed_data["nine"] else 0
    
    average_data["eighteen"] = round(
        mean(summed_data["eighteen"]),
        2
    )if summed_data["eighteen"] else 0
    
    return average_data


def calculate_handicap(data_universe):
    """
    the handicap calculation is complicated. you need to calculate a score
    differential for the 8 most recent rounds played.

    input: data_universe
    input type: dict
    
    output: handicap
    output type: float
    """
    differentials = []
    
    for rnd in data_universe:
        if not rnd["is_nine"]:
            differentials.append(calculate_differential(rnd))
    
    lowest_eight_differentials = sorted(differentials, reverse=True)[:7]
    
    return round(mean(lowest_eight_differentials),0)

def calculate_differential(rnd):
    """
    slope divisor / slope of course * (score - course rating)
    """
    
    score = sum([i["SCORE"] for i in rnd["data"]])
    course = rnd["data"][0]["COURSE"]
    course_slope = COURSES_INFO[course]["slope"]
    course_rating = COURSES_INFO[course]["rating"]
    
    differential = abs((SLOPE_DIVISOR / course_slope) * (score - course_rating))
    
    return differential

################################# UTILITIES ###################################

def pstop(msg):
    raise Exception(pretty_print.pretty_print(msg))

if __name__ == "__main__":
    main()