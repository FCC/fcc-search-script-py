import sys
import os
import pysolr
import datetime
import pytz
import xlwt
from datetime import timezone
from calendar import monthrange

sru = __import__('search-report-util')

solr_host = sys.argv[1]
month_to_report = sys.argv[2] # YYYYMM format
facet_limit = sys.argv[3]

year = int(month_to_report[:4])
month = int(month_to_report[4:])
_, days_in_month = monthrange(year, month)

solr = pysolr.Solr('http://' + solr_host + '/solr/history/', timeout=30)

book = xlwt.Workbook()

sheets = ['Overall', 'FCC.gov', 'EDOCS', 'OPIF']
t = {'Overall': None, 'FCC.gov': 'web', 'EDOCS': 'edocs', 'OPIF': 'opif'}

for sheet in sheets:
    sh = book.add_sheet(sheet, cell_overwrite_ok=True)
    sh.write(0, 0, sheet + ' searches')
    sh.write(2, 4, 'Dates')
    sh.write(4, 4, 'Total searches per day')

    sheet_q_values = {}
    sheet_day_q_values = {}
    sheet_day_counts = {}

    for day in range(1, days_in_month):
        count, facets = sru.count_and_facet_array(solr, t[sheet], sru.full_day_date_clause(year, month, day), 'qUntokenized', facet_limit)
        sheet_day_counts[day] = count
        # facets is a list of alternating query strings and counts. Has even number of elements
        day_q_values = {}

        for fit in range(0, len(facets), 2):
            day_q_values[facets[fit]] = facets[fit + 1]
            if not (facets[fit] in sheet_q_values):
                sheet_q_values[facets[fit]] = 1

        sheet_day_q_values[day] = day_q_values
    # write daily stats
    for day in range(1, days_in_month):
        sh.write(2, 4 + day, str(year) + '-' + str(month) + '-' + str(day))
        row = 6
        for key, value in sheet_q_values.items(): 
            sh.write(row, 4, key)
            if key in sheet_day_q_values[day]:
                sh.write(row, 4 + day, sheet_day_q_values[day][key])
            row += 1  
        sh.write(4, 4 + day, sheet_day_counts[day])

    # write monthly stats
    count, facets = sru.count_and_facet_array(solr, t[sheet], sru.full_month_date_clause(year, month), 'qUntokenized', facet_limit)
    sh.write(4, 1, 'Monthly Top ' + str(facet_limit))

    row = 6
    for fit in range(0, len(facets), 2):
        sh.write(row, 1, facets[fit])
        sh.write(row, 2, facets[fit + 1])
        row += 1

book.save(month_to_report + '-' + pytz.timezone('US/Eastern').localize(datetime.datetime.now()).isoformat().replace(':', '.') + '.xls')

