#!/usr/bin/env python3
"""
This script reads in a CSV, attempts to parse the timestamp, and writes out a CSV file with the timestamp changed to the specified format. This script assumes the CSV has a header and the corresponding column number must for the timestamp must be specified. If no output date format is given, YYYY-MM-DD and 24 hour format is default. The default expected input date is DD/MM/YYYY.

There is NO GUARANTEE that the script will parse the timestamp 'correctly' - e.g. 01/05/2020 is ambiguous between the 1st of May or the 5th of January. By default, this script will interpret DD/MM ordering and so parse this as the 1st of May. If you know what the date formatting for the file is expected to be, specify it with -e. E.g. -e DD/MM/YYYY will make the script interpret 01/05/2020 as May 1st, while -e MM/DD/YYYY will make the script interpret it as the 5th of January.

The timestamps in the file should preferably have four characters for year (e.g. 2020). If only the year is only specified with two characters (e.g. 20), it is best to use -e to specify the ordering of year-month-day. If you have mixed encodings (e.g. DD/MM/YYYY and MM/DD/YYYY), the script will parse both of them according to the expected ordering, except in the case of impossible dates; the script will automatically change dates with an impossible alternative even if expected output is specified. E.g. 12/13/2020 and 13/12/2020 will both be interpreted as 2020-12-13 (Dec 13th) regardless of what is specified with -e.

The script can also take a specified date that serves as the latest acceptable date. If a timestamp occurs after the specified latest date, the script will attempt to swap the month and day numbers on the assumption that they were incorrectly ordered. If this swap is acceptable, the new timestamp will be written into the output CSV. If the swap is not acceptable, the original timestamp will be written out. If this occurs and you were not expecting it, you may have mixed date encodings in your input CSV file. The changed rows will be written to stdout - make sure to check them to see that the date parsed correctly.
"""

import sys


from argparse import ArgumentParser
from csv import reader, writer, Sniffer
from dateutil.parser import parse

def attemptDateCorrection(parsedTimestamp, newRow, latestDate, timestamp, timestampCol, rowNum, yearFirst, dayFirst, dateOutput):
	sys.stdout.write(f"WARNING: {timestamp} parsed as {parsedTimestamp} in row {rowNum + 2} occurs after {latestDate}. Attempting to change... ")
	splitTimestamp = timestamp.split(" ")
	splitDate = splitTimestamp[0]
	splitTime = splitTimestamp[1]

	if "/" in splitDate and "-" not in splitDate:
		splitSplitDate = splitDate.split("/")
	elif "-" in splitDate and "/" not in splitDate:
		splitSplitDate = splitDate.split("-")
	else:
		sys.stderr.write(f"ERROR: {splitDate} contains both '-' and '/'.\n")
		raise Exception("Mixed formatting error")
		
	findSwitches = [x for x in splitSplitDate if len(x) <= 2]
	newTimestamp = ""

	if yearFirst and len(findSwitches) == 3:
		switchOne = 1
		switchTwo = 2
	else:
		switchOne = 0
		switchTwo = 1

	for item in splitSplitDate:
		if item == findSwitches[switchOne]:
			newTimestamp += findSwitches[switchTwo] + " "
		elif item == findSwitches[switchTwo]:
			newTimestamp += findSwitches[switchOne] + " "
		else:
			newTimestamp += item + " "

		newTimestamp = newTimestamp.strip().replace(" ", "/") + " " + splitTime
		parsedNewTimestamp = parse(newTimestamp, dayfirst=dayFirst, yearfirst=yearFirst)

		if parsedNewTimestamp < latestDate:
			sys.stdout.write(f"Success! {parsedNewTimestamp} is a valid date, changing timestamp.\n")
			swappedRow = newRow[:timestampCol]
			swappedRow.append(parsedNewTimestamp.strftime(dateOutput))
			swappedRow.extend(newRow[timestampCol + 1:])

			return swappedRow
		else:
			sys.stdout.write(f"Failure! Timestamp in row {rowNum + 2} must be manually fixed.\n")
			return newRow

def formatCheck(firstRow, timestampCol):
	firstTimestamp = firstRow[timestampCol]
	firstTimestamp = firstTimestamp.split(" ")
	firstDate = firstTimestamp[0]

	if "/" in firstDate and "-" not in firstDate:
		splitFirstDate = firstDate.split("/")
	elif "-" in firstDate and "/" not in firstDate:
		splitFirstDate = firstDate.split("-")
	else:
		sys.stderr.write(f"ERROR: {firstDate} contains both '-' and '/'.\n")
		raise Exception("Mixed formatting error")
		
	twoCharPairs = [x for x in splitFirstDate if len(x) <= 2]
		
	if len(twoCharPairs) > 2:
		sys.stdout.write(f"WARNING: year is specified as YY instead of YYYY. If expected date is not specified and/or mixed encodings are present, YY may be interpreted as MM or DD.\n")

	return None

def createDateOutput(expectedFormat, dateFormat, hourFormat, latestDate):

	if "-" in expectedFormat:
		expectedFormat = expectedFormat.split("-")
	elif "/" in expectedFormat:
		expectedFormat = expectedFormat.split("/")
	else:
		sys.stderr.write(f"ERROR: {expectedFormat} contains both '-' and '/'.\n")
		raise Exception("Mixed formatting error")

	if expectedFormat[0] == "YYYY":
		yearFirst = True
	else:
		yearFirst = False

	if (expectedFormat[1] == "DD" and yearFirst) or (expectedFormat[0] == "DD" and not yearFirst):
		dayFirst = True
	else:
		dayFirst = False

	if "/" in dateFormat:
		delimiter = "/"
	else:
		delimiter = "-"

	if latestDate:
		latestDate = parse(latestDate)
		dateCheckFlag = True
	else:
		dateCheckFlag = False

	if hourFormat == 24:
		hourOutput = "%H:%M"
	elif hourFormat == 12:
		hourOutput = "%I:%M %p"

	if dateFormat == "YYYY/MM/DD" or dateFormat == "YYYY-MM-DD":
		dateOutput = "%Y" + delimiter + "%m" + delimiter + "%d" + " " + hourOutput
	elif dateFormat == "MM/DD/YYYY" or dateFormat == "MM-DD-YYYY":
		dateOutput = "%m" + delimiter + "%d" + delimiter + "%Y" + " " + hourOutput
	elif dateFormat == "DD/MM/YYYY" or dateFormat == "DD-MM-YYYY":
		dateOutput = "%d" + delimiter + "%m" + delimiter + "%Y" + " " + hourOutput
	else:
		sys.stdout.write("Format not recognised, assuming ISO.\n")
		dateOutput = "%Y" + delimiter + "%m" + delimiter + "%d" + " " + hourOutput

	checkFormatWarning = "->".join([x[0] for x in expectedFormat])
	sys.stdout.write(f"Outputting date in format: {dateFormat}.\nDates in input file are being read in order: {checkFormatWarning}.\n")

	formatTuple = (dateOutput, dateCheckFlag, dayFirst, yearFirst, latestDate)

	return formatTuple


def main():
	parser = ArgumentParser(usage=__doc__)
	parser.add_argument('input', metavar='File name', help='A CSV file')
	parser.add_argument('-t', dest='timestampCol', metavar='Timestamp Column', help='Timestamp column number', required=True, type=int)
	parser.add_argument('-df', dest='dateFormat', metavar='Date format', default='YYYY-MM-DD', help='The format of the date you want outputted', choices=["YYYY-MM-DD", "YYYY-DD-MM", "DD-MM-YYYY", "MM-DD-YYYY", "YYYY/MM/DD", "YYYY/DD/MM", "DD/MM/YYYY", "MM/DD/YYYY"])
	parser.add_argument('-hf', dest='hourFormat', metavar='Hour format', default=24, help='24 or 12 hour format', type=int, choices=[24, 12])
	parser.add_argument('-ld', dest='latestDate', metavar='YYYY-MM-DD', help='Latest acceptable date in format: YYYY-MM-DD or YYYY/MM/DD')
	parser.add_argument('-o', dest='fileOutput', metavar='Output', default='output', help='Optional Filename')
	parser.add_argument('-e', dest='expectedFormat', metavar='Expected Format', default='DD-MM-YYYY', help='The date format the file is/should be in e.g. MM-DD-YYYY or DD/MM/YYYY', choices=["YYYY-MM-DD", "YYYY-DD-MM", "DD-MM-YYYY", "MM-DD-YYYY", "YYYY/MM/DD", "YYYY/DD/MM", "DD/MM/YYYY", "MM/DD/YYYY"])
	args = parser.parse_args()

	fileInput = args.input
	fileOutput = args.fileOutput + ".csv"
	latestDate = args.latestDate
	dateFormat = args.dateFormat
	hourFormat = args.hourFormat
	expectedFormat = args.expectedFormat
	timestampCol = args.timestampCol - 1

	dateOutput, dateCheckFlag, dayFirst, yearFirst, latestDate = createDateOutput(expectedFormat, dateFormat, hourFormat, latestDate)

	with open(fileInput, newline='') as csvfile:
		csvReader = reader(csvfile)

		try:
			csvWriter = writer(open(fileOutput, 'x'))
		except FileExistsError as e:
			sys.stderr.write(f"ERROR: {fileOutput} already exists.")
			raise e
		
		#increment twice to grab the first timestamp to check its formatting
		next(csvReader)
		firstRow = next(csvReader)

		formatCheck(firstRow, timestampCol)

		csvfile.seek(0)
		header = next(csvReader)
		csvWriter.writerow(header)

		for i, row in enumerate(csvReader):
			timestamp = row[timestampCol]

			try:
				parsedTimestamp = parse(timestamp, dayfirst=dayFirst, yearfirst=yearFirst)
			except ValueError as e:
				sys.stderr.write(f"ERROR: {timestamp} is not a valid date!\n")
				raise e

			timestampOut = parsedTimestamp.strftime(dateOutput)

			newRow = row[:timestampCol]
			newRow.append(timestampOut)
			newRow.extend(row[timestampCol + 1:])

			if dateCheckFlag and (parsedTimestamp > latestDate):
				rowNum = i
				attemptRow = attemptDateCorrection(parsedTimestamp, newRow, latestDate, timestamp, timestampCol, rowNum, yearFirst, dayFirst, dateOutput)
				csvWriter.writerow(attemptRow)
			else:
				csvWriter.writerow(newRow)

		sys.stdout.write(f"Data written to {fileOutput}\n")


if __name__ == '__main__':
	main()
