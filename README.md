# soccer_tickets
# Pittsburgh Riverhounds Ticket Sales Research 

## Data Sources 
2023 Sales: representative of the 2023 ticket sales 
2024 Sales: representative of the 2024 ticket sales 

Both datasets contained entries for each purchase made. Each entry corresponded with columns that depicted information on which game the ticket was purchased for, the name of the purchaser, the seat location, the number of tickets purchased, when and where the ticket was purchased, the type of ticket purchased, and the price of the purchase (for both the individual seat and the purchase as a whole).


## The Purpose of This Research
This research analyzes nearly 60,000 ticket purchases to identify trends in customer demographics and purchase patterns across the Riverhounds 2023-2024 regular season games. With the information obtained from the study, the Riverhounds can determine which marketing strategies are working and which need improvements, which types of tickets are producing the greatest profit, which event nights effectively increase sales (if any), and generally understand who their audience is to help retain these fans and bring in new ones. 

## Aspects of the Project 
This project contains different research areas including the timing of purchases, the purchaser (who purchased the ticket and where they are from), the type and number of tickets being sold, etc.. 

## Data Cleaning/ Building Reader 
One of the major areas of data cleaning involved the purchaser's zipcode. Because the zipcodes were originally read in as strings,
leading zeroes were deleted from the entry (e.g. an entry such as "00189" was read in as "189"). This lead to innaccurate zipcode representations. Additionally, some zipcodes contained too many numbers and non numerical values. Entries that were able to be formatted correctly were saved to both zipcodes as integers and zipcodes as strings. Others were dropped from the analysis to ensure accurate results.
The integer zipcodes were used to determine the state of purchase and columns representing the state, state abbreviation, and whether or not it was an in or out of state purchase. Additionally, when looking at primarily questions regarding zipcode, tickets bought through large ticketing companies were dropped, as they did not reflect the true purchase area. For questions that were not affected by zipcdoe, these entries were kept for the analysis. 

Another area that required restructuring was ticket types. There was a large variety of categories, with some holding more importance than others. Because of this different columns were created for different areas of analysis that grouped ticket types into larger, simpler categories based on the companies standards.

Further, time of purchase is a large area of interest in the research, so cleaning and standardizing both purchase dates and game dates
was an important step. This was used to examine when particular ticket types see the greatest number of purchases and if there is a trend 
among the timing of tickets purchased different ticket types, areas of purchase, and ticket sales as a whole. 

Lastly, the company was truly interested in regular season purchases, so game types were filtered to exclude playoff and cup games from the analysis.


