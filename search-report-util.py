import pysolr
import datetime
import pytz
from datetime import timezone
from calendar import monthrange

month_to_date_clause = '[NOW-1MONTH/MONTH TO NOW]'
last_30_days_clause = '[NOW-30DAY/DAY TO NOW]'

def fq_for_core(core):
    if not core:
        return ''
    elif core == 'web':
        return '(* -t:[* TO *]) || (* +t:web)'
    else:
        return 't:' + core

def count_and_facet_array(solr, core, date_clause, facet, facet_limit):
    results = solr.search('*:*', **{
        'fq': ['doctype:request', 'runts:' + date_clause, fq_for_core(core)],
        'facet': 'true',
        'facet.field': facet,
        'facet.limit': facet_limit,
        'facet.mincount': 1
    })
    # print(dir(results))
    return results.hits, results.facets['facet_fields'][facet]

def day_back_date_clause(offset):
    if offset == 0:
        return '[NOW-' + str(offset + 1) + 'DAY/DAY TO NOW]'
    else:
        return '[NOW-' + str(offset + 1) + 'DAY/DAY TO NOW-' + str(offset) + 'DAY/DAY]'

def utc_date_string_z(year, month, day, h, m, s, ms):
    eastern = pytz.timezone('US/Eastern')
    return eastern.localize(datetime.datetime(year, month, day, h, m, s, ms)).astimezone(pytz.utc).isoformat().replace('+00:00', 'Z')
    
def full_day_date_clause(year, month, day):
    date_start = utc_date_string_z(year, month, day, 0, 0, 0, 0)
    date_end   = utc_date_string_z(year, month, day, 23, 59, 59, 999999)                                                                                          
    return '[' + date_start + ' TO ' + date_end + ']'

def full_month_date_clause(year, month):
    _, days_in_month = monthrange(year, month)
    date_start = utc_date_string_z(year, month, 1, 0, 0, 0, 0)
    date_end   = utc_date_string_z(year, month, days_in_month, 23, 59, 59, 999999)                                                                                          
    return '[' + date_start + ' TO ' + date_end + ']'

