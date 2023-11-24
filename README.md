# Generate Worked All States (WAS) List from ADIF

This program generates a list of US states and optionally Canadian provinces/territories that have been confirmed, a list of unconfirmed prefectures, and a mapchartSave.txt file for upload to https://www.mapchart.net/usa.html or https://www.mapchart.net/usa-and-canada.html to visualize the states or the states/provinces/territories.

ARRL WAS rule #4 states, "Contacts must be made from same location, or from locations no two of which are more than 50 miles (80 kilometers) apart." Therefore the waslist program requires the user to enter a grid square using the -g switch in order to establish the circle center the program determines the distance from this location and the <MY_GRIDSQUARE> tag to generate the list.  

The following ADIF tags in the file being analyzied are used:
- \<STATION_CALLSIGN>  Your callsign; Optional, Needed for -c option
- \<MY_GRIDSQUARE> Your grid square; Required
- \<STATE> Prefecture of station worked; Required
- \<DXCC> DXCC entity of station worked; Required
- \<MODE> Mode used; Optional, Needed for -m option
- \<BAND> Band used; Optional, Needed for -b option
- \<SAT_NAME> Name of satellite used; Optional, needed for -s option
- \<PROP_MODE> Propagation mode; Optional, needed for --satonly and --nosat options

This can be obtained by using the ARRL Logbook of the World Query by 
Rick Murphy K1MU found at URL: https://www.rickmurphy.net/lotwquery.htm

Use the following settigs when Querying LoTW for your contact records:
* Include worked station location data in report?	 	YES
* Include operator location data in report?	 	YES
* Include owner callsign in report? YES

If the lotwreport.adi downloaded from LoTW contains non UTF-8 characters, use the iconv utility to remove them.

>  iconv -f utf-8 -t utf-8 -c lotwreport.adi > log.adi

Information about ARRL Worked All States Award can be found here: http://www.arrl.org/was

## Requirements

- https://pypi.org/project/argparse/
- https://pypi.org/project/adif-io/
- https://pypi.org/project/pyhamtools/

usa_states.txt and ve_provinces.txt must be co-located in the same folder with the .exe or .py file.

## Installation


## Usage

usage: waslist.py [-h] -g GRID [-c CALL [CALL ...]] [-b BAND] [-m MODE] [-s SAT] [--satonly] [--nosat] [--canada] [--dc] filename

positional arguments:
  filename              LoTW ADIF

options:
  - -h, --help            show this help message and exit
  - -g GRID, --grid GRID  list only contacts made within 50 miles (80 kilometers) of this grid
  - -c CALL [CALL ...], --call CALL [CALL ...] list of callsigns, if not specified all callsigns are considered
  - -b BAND, --band BAND  band (eg. 20M, 2M, 70CM, etc...), if not specified all bands are considered
  - -m MODE, --mode MODE  mode (eg. CW, SSB, FT8, etc...), f not specified all modes are considered
  - -s SAT, --sat SAT     satellite name (eg. RS-44, IO-117, etc...), if not specified all satellites are included
  - --satonly             include only satellite QSOs
  - --nosat               exclude satellite QSOs
  - --canada              include Canadian provinces/territories
  - --dc                  include District of Colombia

## Related Projects


## Credits


## License

[MIT](LICENSE) © [kilo8deltapapa](https://github.com/kilo8deltapapa).
