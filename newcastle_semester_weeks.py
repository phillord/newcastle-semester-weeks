#!/usr/bin/python

## requires installation on ubuntu "python-icalendar
from icalendar import Calendar, Event
from datetime import date
from datetime import timedelta
import numbers

## format is week commencing, teaching week.
## If teaching week is a string, then is used instead. So
## blank for before term, or vacation, or exam
##
## Simple consecutive weeks can be missed off.
cal = [
    ## 2014-15
    ["2014-09-01","Pre Semester 1"],
    ["2014-09-29",1],
    ["2014-12-15","Vacation"],
    ["2015-01-05",12],
    ["2015-01-12","Assessment"],
    ["2015-01-26",1],
    ["2015-03-16","Vacation"],
    ["2015-04-13",8],

    ["2015-05-11",12],
    ["2015-05-18","Vacation"],

    ## 2015-16
    ["2015-08-31", "Pre Semester 1"],
    ["2015-10-05", 1],
    ["2015-12-21", "Vacation"],
    ["2016-01-11", 12],
    ["2016-01-18", "Assessment"],
    ["2016-02-01", 1],
    ["2016-03-14", "Vacation"],
    ["2016-04-11", 7],
    ["2016-05-23", "Vacation"]

    ## need to finish the last year with week 12, or the next will crash
    ## Also, there is a ticker below at 104 weeks which needs updating
    ]


## user configuration stops here


## return the date a week later than date
def add_one(date):
    return date + timedelta(days=1)

def add_week(date):
    return date + timedelta(days=7)

def string_date(date):
    return date.strftime("%Y-%m-%d")

def parse_date(date_str):
    splt = map(int,date_str.split("-"))
    return date(splt[0],splt[1],splt[2])
    ##return datetime.strptime( date_str, "%Y-%m-%d")

def is_monday(date):
    return date.weekday() == 0

## switch string objects through to datetime objects
def datetime_ify(cal_config):
    return [[parse_date(d[0]),d[1]] for d in cal_config]

def lint_calendar(cal):

    #last_calendar_week = 0
    last_semester_week = 0
    semester = 1

    for d in cal:
        ## tell me why, I like Mondays?
        if(not is_monday(d[0])):
            raise Exception("The date {} is not on a monday".
                            format(string_date(d[0])))

        # ## calendar weeks should always go up
        # if(d[1] < last_calendar_week):
        #     raise Exception("Calendar Weeks {} and {} are not increasing".
        #                     format(d[1], last_calendar_week) )
        # else:
        #     last_calendar_week = d[1]

        ## semester weeks should always go up
        if(type(d[1]) is int):
            if(d[1] == 12 ):
                last_semester_week = 0
            elif( d[1] < last_semester_week ):
                raise Exception("Semester Weeks {} and {} are not increasing".
                                format(d[1], last_semester_week) )
            elif(d[1] > 12):
                raise Exception("Illegal semester week:{}".format(d))
            else:
                last_semester_week = d[1]


    return cal


def interpolate_calendar(cal):
    ## clone for safety, and get return read
    cal_clone = list(cal)
    retn_cal = []

    working_week = cal_clone.pop(0)

    for calendar_week in range(0,104):
        ## add the working week
        retn_cal.append(working_week)
        ## stuff on the calendar week
        working_week.append(calendar_week % 52 + 1)
        ## increment the semester week for next time!
        if(type(working_week[1]) is int):
            ## clone working week
            working_week = list(working_week)
            working_week[1] = working_week[1] + 1

        ## work out the date after the current working week
        one_week_ahead = add_week(working_week[0])

        ## if there is a next element left on the calendar config
        ## and it's date is identical, then just use that instead
        if(len(cal_clone)>0 and
           one_week_ahead==cal_clone[0][0]):
            working_week = cal_clone.pop(0)
        else:
            working_week = [one_week_ahead,working_week[1]]

    return retn_cal

def display(cal):
    return cal.to_ical().replace('\r\n', '\n').strip()


## first, go through date set and lint
## all dates start on monday
datetime_cal = lint_calendar(datetime_ify(cal))
datetime_full = lint_calendar(interpolate_calendar(datetime_cal))

ical = Calendar()
ical.add("summary","Newcastle University Semester Weeks")
## cache for no time
ical.add("X-PUBLISHED-TTL","PT1M")
ical.add("REFRESH-INTERVAL","PT1M")
ical.add("name","Newcastle University Semester Weeks")

semester = 1
for e in datetime_full:
    eve = Event()
    summary = ""
    if( type(e[1]) == int ):
        summary = "Semester:{} Week:{} Cal:{}".format(semester,e[1],e[2])
        if(e[1] == 12 ):
            if(semester == 1):
                semester = 2
            else:
                semester = 1
    else:
        summary = "{} Cal:{}".format(e[1],e[2])

    eve.add("summary",summary)
    eve.add("dtstart",e[0])
    ## dtstop makes outlook work
    eve.add("dtstop", add_one(e[0]))
    ## google calendar seems to like end
    eve.add("dtend", add_one(e[0]))
    eve.add("rrule",{"freq":"daily","count":"5"})
    ical.add_component(eve)

print display(ical)
