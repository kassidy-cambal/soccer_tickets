import pandas as pd # good for excel
import os 
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import seaborn as sns

# build fns and processing into reader 
# dont have to save intermediate files 

class Reader():
    def __init__(self, sales23, sales24, drop_bulk = False):
        """Read in sales data for 2023-2024"""
        self.sales23 = sales23
        self.sales24 = sales24
        self.total_sales = None  # Initialize an empty attribute
        self._concatenate_sales()
 
        if self.total_sales is not None:

            # creates a new column for gametype: regular, playoff, cup
            self.total_sales['game_type'] = self.total_sales['event_name'].apply(self._set_gametypes) 

            # takes the first five of the string of zipcode 
            self.total_sales['cleaned_zip'] = self.total_sales['zip'].apply(self._cleaning_zipcodes)


            # this converts the cleaned zipcode to an integer to determine range for state 
            # self.total_sales['cleaned_zip'] = self.total_sales['cleaned_zip'].apply(lambda x: self._to_Integer(x, self.exclude_value))
            self.total_sales['zip_as_int'] = self.total_sales['cleaned_zip'].apply(self._zip_To_Integer)

            # corrects leading zeroes in zipcodes
            self.total_sales['zip_as_str'] = self.total_sales['zip_as_int'].apply(self.fixZeros)

            # determines the state of purchaser 
            self.total_sales['purchase_state'] = self.total_sales['zip_as_int'].apply(self._determining_state)

            
            self.total_sales['In_or_Out'] = self.total_sales['purchase_state'].apply(self._PA_or_no)

            self.total_sales['purchase_abbreviations'] = self.total_sales['purchase_state'].apply(self._purchase_state_abbreviations)

            self.total_sales['opponent'] = self.total_sales['event_name'].apply(self._opponent)

            self.total_sales['opponent_state'] = self.total_sales['event_name'].apply(self._opponent_State)

            # drops columns we arent using 
            self._drop_columns()

            # adding a column for date of the game 
            self.total_sales['game_date'] = self.total_sales['event_name'].apply(self._game_date)

            # changing purchase date to datetime format 
            self.total_sales['purchase_date'] = self.total_sales['add_datetime'].apply(self._timestamp_fix)

            self.total_sales.apply(self._timestamp_two_fix)
            

            # adding column for how far out ticket was purchase d
            self.total_sales['days_out'] = self.total_sales.apply(self._days_out, axis = 1)

            # keeps only the entries from the regular season, drops playoff and cup games 
            self.total_sales = self._regular_season()

            self.total_sales['updated_ticket_type'] = self.total_sales['ticket_type'].apply(self._ticket_type)

            self.total_sales['simple_ticket_type'] = self.total_sales['updated_ticket_type'].apply(self.simpler_ticket_types)

            # drops the Tix, Vet and Optimal Ticketing 
            # self.total_sales = self._ticket_companies()

        # self._clean_df_columns()
        # self._clean_data()


    def _concatenate_sales(self):
        """This will concatenate the 2023 and 2024 sales data and will create a binary column
        called year.
        """
        if os.path.exists(self.sales23) and os.path.exists(self.sales24):
            sales23 = pd.read_csv(self.sales23)
            sales24 = pd.read_csv(self.sales24, encoding = 'latin1')
            sales23['year'] = 0 
            sales24['year'] = 1
            self.total_sales = pd.concat([sales23, sales24], ignore_index = True)
        else:
            print("One or both sales files are missing.")
            self.total_sales = pd.DataFrame()

    def _set_gametypes(self, event_code):
        """This will loop through the event codes to classify a game as regular, playoff, or cup. 
        The value will be stored in a new column called "game_type".
        """

        regularSeason23 = ['23RH0324', '23RH0415', '23RH0513', '23RH0520', '23RH0603',
        '23RH0610', '23RH0624', '23RH0701', '23RH0708', '23RH0715',
        '23RH0726', '23RH0729', '23RH0805', '23RH0812', '23RH0909',
        '23RH0923', '23RH0930', '23RH0425']

        playoff23 = ['23RHPL1']

        cup23 = ['23RHCUP5']

        regularSeason24 = ['24RH0316', '24RH0406', '24RH0427', '24RH0504', '24RH0518',
        '24RH0601', '24RH0619', '24RH0706', '24RH0713', '24RH0720',
        '24RH0727', '24RH0810', '24RH0817', '24RH0907', '24RH0928',
        '24RH1012', '24RH1026']

        playoff24 = []

        cup24 = ['24RHCUP4']

        if (event_code in regularSeason23) or (event_code in regularSeason24):
            return "regular"
        elif (event_code in playoff23) or (event_code in playoff24):
            return "playoff"
        elif (event_code in cup23) or (event_code in cup24):
            return "cup"

        
    def _cleaning_zipcodes(self, zip ):
        """This will create a new column that stores corrected zip codes.
        The original zipcode column contained zipcodes with an invalid 
        number of numbers, contained letters, or contained special characters.
        """
        if pd.isna(zip):
            return "nan"
        zip = str(zip)
        zip = zip[:5]
        return zip

    def fixZeros(self, string):
        """This adds additional zeroes to the beginning of zipcodes 
        Because the zipcodes were stored as integers, leading zeroes were originally removed 
        """

        string = str(string)
        if string == "nan":
            return "nan"
        if len(string) == 5:
            return string
        if len(string) == 4:
            return("0" + string)
        if len(string) == 3:
            return("00" + string)
        if string == "0":
            return "nan"

 
    def _contains_A_Letter(self, s, excludeString = 'nan'):
        """This loops through entries letter by letter to determine if there is an alphabetic letter"""
        found = False
        for x in s:
            if x.isalpha():
                found = True
        return found 
    


    # Function converts value to an int if it doesnt equal a given value 
    def _zip_To_Integer(self, value, exclude_value = 'nan'):
        found = False
        for x in value:
            if x.isalpha():
                found = True
        # return found 
        if found == True: 
            return exclude_value 
        else:
            return int(value)
        # if value != exclude_value:
        #     return int(value)
        # else:
        #     return exclude_value  

    # Applying the toInteger function to the cleaned_zip column
    # converts zip codes that arent nan to an integer so that we can check the range to determine state
    # exclude_value = 'nan'


       
    def _determining_state(self, zip):
        """This takes in a zip code and returns the state depending on what range the zip code is in"""
        if zip != "nan":
            if zip in range (99501,99951):
                return("Alaska")
            elif zip in range(35004,36926):
                return "Alabama"
            elif (zip in range(71601,72960)) or zip == 75502:
                return "Arkansas"
            elif zip in range(85001,86557):
                return "Arizona"
            elif zip in range(90001,96162):
                return "California"
            elif zip in range(80001,81659):
                return "Colorado"
            elif (zip in range(6001,6390)) or (zip in range(6401,6929)):
                return "Connecticut"
            elif (zip in range(20001,20040)) or (zip in range(20042,20600)) or (zip == 20799):
                return "District of Columbia"
            elif zip in range(19701, 19981):
                return "Delaware"
            elif zip in range(32004,34998):
                return "Florida"
            elif (zip in range(30001,32000)) or (zip == 39901):
                return "Georgia"
            elif zip in range(96701,96899):
                return "Hawaii"
            elif (zip in range(50001,52809)) or (zip in range(68119, 68121)):
                return "Iowa"
            elif zip in range(83201,83877):
                return "Idaho"
            elif zip in range(60001,63000):
                return "Illinois"
            elif zip in range(46001,47998):
                return "Indiana"
            elif zip in range(66002,67955):
                return "Kansas"
            elif zip in range(40003,42789):
                return "Kentucky"
            elif (zip in range(70001,71233)) or (zip in range(71234,71498)):
                return "Louisiana"
            elif (zip in range(1001,2792)) or (zip in range(5501,5545)):
                return "Massachusetts"
            elif (zip == 20331) or (zip in range(20335,20798)) or (zip in range(20812,21931)):
                return "Maryland"
            elif zip in range(3901,4993):
                return "Maine"
            elif zip in range(48001,49972):
                return "Michigan"
            elif zip in range(55001,56764):
                return "Minnesota"
            elif (zip in range(38601,39777)) or (zip == 71233):
                return "Mississippi"
            elif zip in range(59001,59938):
                return "Montana"
            elif zip in range(27006,28910):
                return "North Carolina"
            elif zip in range(58001,58857):
                return "North Dakota"
            elif (zip in range(68001,68119)) or (zip in range(68122, 69368)):
                return "Nebraska"
            elif zip in range(3031,3898):
                return "New Hampshire"
            elif zip in range(7001,8990):
                return "New Jersey"
            elif zip in range(87001,88442):
                return "New Mexico"
            elif zip in range(88901,89884):
                return "Nevada"
            elif (zip in range(10001,14976)) or (zip == 6390):
                return "New York"
            elif zip in range(43001,46000):
                return "Ohio"
            elif (zip in range(73001,73200)) or (zip in range(73401,74967)):
                return "Oklahoma"
            elif zip in range(97001,97921):
                return "Oregon"
            elif zip in range(15001,19641):
                return "Pennsylvania"
            elif zip in range(2801,2941):
                return "Rhode Island"
            elif zip in range(29001,29949):
                return "South Carolina"
            elif zip in range(57001,57800):
                return "South Dakota"
            elif zip in range(37010,38590):
                return "Tennessee"
            elif (zip in range(75001,75502)) or (zip in range(75503,80000)) or (zip in range(88510,88590)) or (zip == 73301):
                return "Texas"
            elif zip in range(84001,84785):
                return "Utah"
            elif (zip in range(20040,20042)) or (zip in range(20040, 20168)) or (zip == 20042) or (zip in range(22001,24659)):
                return "Virginia"
            elif (zip in range(5001,5495)) or (zip in range(5601,5908)):
                return "Vermont"
            elif zip in range(98001,99404):
                return "Washington"
            elif zip in range(53001,54991):
                return "Wisconsin"
            elif zip in range(24701,26887):
                return "West Virginia"
            elif zip in range(82001,83129):
                return "Wyoming"

    

    def _PA_or_no(self, state):
        """This takes in a state name and returns in state or out of state based on state name"""
        if pd.isna(state):
            return "nan"
        else: 
            if state == "Pennsylvania":
                return "In State"
            else:
                return "Out of State"


    def _purchase_state_abbreviations(self, state):
        """This takes in a state and returns state abbreviation based on state name"""
        if state == "Pennsylvania":
            return "PA"
        elif state == "Florida":
            return "FL"
        elif state == "Ohio":
            return "OH"
        elif state == "Arizona":
            return "AZ"
        elif state == "West Virginia":
            return "WV"
        elif state == "Michigan":
            return "MI"
        elif state == "New York":
            return "NY"
        elif state == "New Jersey":
            return "NJ"
        elif state == "Virginia":
            return "VA"
        elif state == "Maryland":
            return "MD"
        elif state == "Texas":
            return "TX"
        elif state == "California":
            return "CA"
        elif state == "North Carolina":
            return "NC"
        elif state == "District of Columbia":
            return "DC"
        elif state == "Illinois":
            return "IL"
        elif state == "Kentucky":
            return "KY"
        elif state == "Indiana":
            return "IN"
        elif state == "Georgia":
            return "GA"
        elif state == "South Dakota":
            return "SD"
        elif state == "Massachusetts":
            return "MA"
        elif state == "Delaware":
            return "DE"
        elif state == "Colorado":
            return "CO"
        elif state == "South Carolina":
            return "SC"
        elif state == "Tennessee":
            return "TN"
        elif state == "Connecticut":
            return "CT"
        elif state == "Wisconsin":
            return "WI"
        elif state == "Utah":
            return "UT"
        elif state == "Washington":
            return "WA"
        elif state == "Oregon":
            return "OR"
        elif state == "Alabama":
            return "AL"
        elif state == "Louisiana":
            return "LA"
        elif state == "New Mexico":
            return "NM"
        elif state == "Iowa":
            return "IA"
        elif state == "New Hampshire":
            return "NH"
        elif state == "Minnesota":
            return "MN"
        elif state == "Vermont":
            return "VT"
        elif state == "Oklahoma":
            return "OK"
        elif state == "Kansas":
            return "KS"
        elif state == "Idaho":
            return "ID"
        elif state == "North Dakota":
            return "ND"
        elif state == "Mississippi":
            return "MS"
        elif state == "Maine":
            return "ME"
        elif state == "Rhode Island":
            return "RI"
        elif state == "Arkansas":
            return "AR"
        elif state == "Alaska":
            return "AK"
        elif state == "Hawaii":
            return "HI"
        elif state == "Nevada":
            return "NV"
        elif state == "Iowa":
            return "IA"
        elif state == "Nebraska":
            return "NE"
        else:
            return "unknown"




    
    def _opponent(self, string):
        """This takes in an event code and returns who the opponent is"""
        if (string == "23RH0324") or (string == "24RH0504"):
            return "Miami"
        elif string == "23RH0415":
            return "Rio Grande Valley"
        elif (string == "23RH0513") or (string == "24RH0928"):
            return "Birmingham"
        elif string == "23RH0520":
            return "Las Vegas"
        elif string == "23RH0415":
            return "Rio Grande Valley"
        elif string == "23RH0603":
            return "Pheonix"
        elif (string == "23RH0610") or (string == "24RH1012"):
            return "Charleston"
        elif string == "23RH0624":
            return "San Diego"
        elif (string == "23RH0701") or (string == "24RH0619"):
            return "Louisville"
        elif string == "23RH0708":
            return "Sacramento"
        elif string == "23RH0715":
            return "Detroit"
        elif (string == "23RH0726") or (string == "24RH0601"):
            return "Indy"
        elif string == "23RH0729":
            return "Memphis"
        elif (string == "23RH0805") or (string == "24RH0406"):
            return "Tampa Bay"
        elif (string == "23RH0812") or (string == "24RH0720"):
            return "Hartford"
        elif (string == "23RH0909") or (string == "24RH0727"):
            return "Loudon"
        elif string == "23RH0923":
            return "New Mexico"
        elif string == "23RH0930":
            return "Tulsa"
        elif string == "24RH0316":
            return "Orange County"
        elif (string == "24RH0427") or (string == "23RHPL1"):
            return "Detroit FC"
        elif string == "24RH0518":
            return "North Carolina"
        elif string == "24RH0706":
            return "Montery Bay"
        elif string == "24RH0713":
            return "Oakland"
        elif string == "24RH0810":
            return "San Antonio"
        elif string == "24RH0817":
            return "Colorado Springs"
        elif string == "24RH0907":
            return "Rhode Island"
        elif string == "24RH1026":
            return "El Paso"
        elif string == "23RH0425":
            return "Maryland"
        elif (string == "23RHCUP5") or (string == "24RHCUP4"):
            return "cup"



    
    def _opponent_State(self, string):
        """This takes in the event code and returns the state the opponent is from"""
        if (string == "23RH0324") or (string == "24RH0504"):
            return "Florida"
        elif string == "23RH0415":
            return "Texas"
        elif (string == "23RH0513") or (string == "24RH0928"):
            return "Alabama"
        elif string == "23RH0520":
            return "Nevada"
        elif string == "23RH0415":
            return "Texas"
        elif string == "23RH0603":
            return "Arizona"
        elif (string == "23RH0610") or (string == "24RH1012"):
            return "South Carolina"
        elif string == "23RH0624":
            return "California"
        elif (string == "23RH0701") or (string == "24RH0619"):
            return "Kentucky"
        elif string == "23RH0708":
            return "California"
        elif string == "23RH0715":
            return "Michigan"
        elif (string == "23RH0726") or (string == "24RH0601"):
            return "Indianapolis"
        elif string == "23RH0729":
            return "Tennessee"
        elif (string == "23RH0805") or (string == "24RH0406"):
            return "Florida"
        elif (string == "23RH0812") or (string == "24RH0720"):
            return "Connecticut"
        elif (string == "23RH0909") or (string == "24RH0727"):
            return "Tennessee"
        elif string == "23RH0923":
            return "New Mexico"
        elif string == "23RH0930":
            return "Oklahoma"
        elif string == "24RH0316":
            return "California"
        elif (string == "24RH0427") or (string == "23RHPL1"):
            return "Michigan"
        elif string == "24RH0518":
            return "North Carolina"
        elif string == "24RH0706":
            return "California"
        elif string == "24RH0713":
            return "California"
        elif string == "24RH0810":
            return "Texas"
        elif string == "24RH0817":
            return "Colorado"
        elif string == "24RH0907":
            return "Rhode Island"
        elif string == "24RH1026":
            return "Texas"
        elif string == "23RH0425":
            return "Maryland"
        elif (string == "23RHCUP5") or (string == "24RHCUP4"):
            return "cup"



    def _ticket_type(self, ticket):
        """This takes in a ticket type and groups it into smaller groups based on Riverhounds current ticket grouping"""
        single_game_promo = ['Additional Staff', 'Adult $10 Ticket', 'Adult Promo', 'Comp Ticket', 
        'Compt Ticket', 'Corporate Partner', 'Friends of the Riverhounds', 'Upgrade Grandstand',
        'Upgrade Riverside', 'Weather Delay', 'Costco Offer']

        single_game_full = ['Adult', 'Adult A Game', 'Adult B Game', 'Adult C Game', 'Season Additional',
        'Season Adtl. 1 Year', 'Season Adtl. 2 Year', 'Season Deposit', 'Season Steel Army Additional',
        'Season Ticket Holder', 'Premium Single', 'Adult A+ Ticket']
    
        flex = ['Bonus Flex', 'Flex Academy', 'Flex Black Friday', 'Flex Cyber Monday', 'Flex Discount',
        'Flex Fevo', 'Flex Home Opener', 'Flex New', 'Flex Package', 'Flex Renewal', 'Flex Renew',
        'Flex Single Voucher', 'Flex Valentines Day']

        other_promotion = ['Bundle Open Cup', 'Hounds Night Aht', 'May Package', 'Mothers Day', 'Ultimate Fan Pack']

        container = ['Container', 'Corner Additional', 'Corner New', 'Corner Renew']

        groups = ['Group $10 Ticket', 'Group Discounted', 'Group Large', 'Group New',
        'Group Performer', 'Group Renew', 'Group Soccer', 'Group Standard', 'Group Theme',
        'Large New','Large Renew' ]

        fundraiser = ['Group $5 Donation', 'Group Fundraiser']

        birthdays = ['Group Birthday']

        party_deck = ['Party Deck', 'Party Deck Additional', 'Party Deck New', 'Party Deck Renew']

        suite = ['Premium', 'Premium Discounted', 'Suite Additional', 'Suite Last', 'Suite New',
        'Suite Renewal', 'Suite Renew', 'Premium New', 'Premium Additional', 'Premium Renew'] 

        youth_soccer = ['Riverhounds Academy']

        new_season = ['Season New 1 Year', 'Season New 2 Year', 'New 2-Year']

        renew_season = ['Season Renewal 1 Year', 'Season Renewal 2 Year', 'Season Renew 1 Year',
        'Season Renew 2 Year']

        student_rush = ['Student Rush']


        if ticket in single_game_promo:
            return ("single game promo")
        elif ticket in single_game_full:
            return "single game full"
        elif ticket in flex:
            return "flex"
        elif ticket in other_promotion:
            return "other_promotion"
        elif ticket in container:
            return "container"
        elif ticket in groups:
            return "group"
        elif ticket in fundraiser:
            return "fundraiser"
        elif ticket in birthdays:
            return "birthday"
        elif ticket in party_deck:
            return "party deck"
        elif ticket in suite:
            return "suite"
        elif ticket in youth_soccer:
            return "youth_soccer"
        elif ticket in new_season:
            return "new season"
        elif ticket in renew_season:
            return "renew season"
        elif ticket in student_rush:
            return "student rush"

    def simpler_ticket_types(self,ticket):
        if ticket == "group":
            return "group"
        elif ticket == "single game full":
            return "single game full"
        else:
            return "other "


    def _drop_columns(self):
        """This drops the columns that are not relevent to our research
        """
        cols_to_drop = ['acct_id', 'price_code', 'promo_code', 'acct_rep_id', 'assoc_acct_id', 'acct_type_desc', 'add_usr']
        self.total_sales.drop(cols_to_drop, axis = 1, inplace = True)     


    def _game_date(self, code):
        """This takes in the game code and returns the date of the game"""
        if code == '23RH0324':
            return '2023-03-24'
        elif code == '23RH0415':
            return '2023-04-15'
        elif code == '23RH0513':
            return '2023-05-13'
        elif code == '23RH0520':
            return '2023-05-20'
        elif code == '23RH0603':
            return '2023-06-03'
        elif code == '23RH0610':
            return '2023-06-10'
        elif code == '23RH0624':
            return '2023-06-24'
        elif code == '23RH0701':
            return '2023-07-01'
        elif code == '23RH0708':
            return'2023-07-08'
        elif code == '23RH0715':
            return '2023-07-15'
        elif code == '23RH0726':
            return '2023-07-26'
        elif code == '23RH0729':
            return '2023-07-29'
        elif code == '23RH0805':
            return '2023-08-05'
        elif code == '23RH0812':
            return '2023-08-12'
        elif code == '23RH0909':
            return '2023-09-09'
        elif code == '23RH0923':
            return '2023-09-23'
        elif code == '23RH0930':
            return '2023-09-30'
        elif code == '23RH0425':
            return '2023-04-25'
        elif code == '24RH0316':
            return '2024-03-16'
        elif code == '24RH0406':
            return '2024-04-06'
        elif code == '24RH0427':
            return'2024-04-27'
        elif code == '24RH0504':
            return '2024-05-04'
        elif code == '24RH0518':
            return '2024-05-18'
        elif code == '24RH0601':
            return '2024-06-01'
        elif code == '24RH0619':
            return '2024-06-19'
        elif code == '24RH0706':
            return '2024-07-06'

        elif code == '24RH0713':
            return '2024-07-13'
        elif code == '24RH0720':
            return '2024-07-20'
        elif code == '24RH0727':
            return'2024-07-27'
        elif code == '24RH0810':
            return '2024-08-10'
        elif code == '24RH0817':
            return '2024-08-17'
        elif code == '24RH0907':
            return '2024-09-07'
        elif code == '24RH0928':
            return '2024-09-28'
        elif code == '24RH1012':
            return '2024-10-12'
        elif code == '24RH1026':
            return '2024-10-26'
        
    def _timestamp_fix(self, date):
        date_obj = datetime.strptime(date, "%m/%d/%y")
        return(date_obj)
    
    def _timestamp_two_fix(self, date):
        self.total_sales['purchase_date'] = pd.to_datetime(self.total_sales['purchase_date'])
        self.total_sales['game_date'] = pd.to_datetime(self.total_sales['game_date'])

        # self.total_sales['game_date'] = pd.to_datetime(self.total_sales['game_date'])
        # self.total_sales['purchase_date'] = pd.to_datetime(self.total_sales['purchase_date'])

    def _days_out(self, row):
        if row is None:
            return None
        else:
            return (row['purchase_date'] - row['game_date']).days

    def _regular_season(self):
        return self.total_sales[self.total_sales['game_type'] == "regular"]


    def _ticket_companies(self):
        return self.total_sales[~self.total_sales['owner_name'].isin(['Optimal Ticketing', "Tix, Vet"])]
    
    

    # def _clean_df_columns(self):
    #     """Fix column names to be lowercase
    #     """
    #     mapper = {}
    #     # alt shift and drag down to highlight 
    #     # option alt and arrows to shift 
    #     # pass a dictionary to rename function

    #     self.df = self.df.rename(columns = mapper)[mapper.values()] # pulling out only columns we care about 

    # def _clean_data(self):
    #     """Split Names 
    #     """
    #     # string split turns into a list
    #     self.df['pi_names'] = self.df['pi_names'].str.split(';')
    #     self.df = self.df.explode['pi_names'] # breaks a list, some rows duplicated
    #     # each name has own row with rest of data copied to each

    #     self.df['is_contact'] = self.df['pi_names'].str.lower().str.contains('(contact)') # could use .suffix (research this)
    #     self.df['pi_names'] = self.df['pi_names'].str.replace('(contact)','')

if __name__ == '__main__':
    r = Reader('/Users/kassidycambal/Documents/Research/Riverhounds/Data/2023_Sales.csv', '/Users/kassidycambal/Documents/Research/Riverhounds/Data/2024_Sales_as_of_Oct03.csv')
    # print(len(r.total_sales))
    print(r.total_sales.columns)


    # ax = sns.countplot(data = r.total_sales, x = 'In_or_Out', color = 'gold')
    # plt.title("In and Out-of-State Ticket Purchases", fontsize = 18)
    # plt.xticks(fontsize= 12)
    # plt.xlabel('Location', fontsize = 14)
    # plt.grid(True)
    # plt.ylabel('Frequency', fontsize = 14)
    # ax.bar_label(ax.containers[0], label_type='edge', fmt = "%.2f")
    # plt.show()
        

    # print(r.total_sales.dtypes)
    # print(r.total_sales[['purchase_date','add_datetime', 'game_date']])
    