#!/usr/bin/python

## requires installation on ubuntu "python-icalendar
from icalendar import Calendar, Event
from datetime import date
from datetime import timedelta
import numbers

## format is week commencing, teaching week, calendar week.
## If teaching week is a string, then is used instead. So
## blank for before term, or vacation, or exam
##
## Simple consecutive weeks can be missed off.
cal = [
    ## 2014-15
    ["2014-09-01","Pre Semester 1",1],
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
    ["2015-09-07", "Pre Semester 1", 1],
    ["2015-10-05", 1],
    ["2015-12-21", "Vacation"],
    ["2016-01-11", 12],
    ["2016-01-18", "Assessment"],
    ["2016-02-01", 1],
    ["2016-03-14", "Vacation"],
    ["2016-04-11", 7],
    ["2016-05-16", 12],
    ["2016-05-23", "Vacation"],
    ## need to finish the last year with week 12, or the next will crash

    ## 2016-17
    ["2016-09-05", "Pre Semester 1", 1],
    ["2016-10-03", 1],
    ["2016-12-19", "Vacation"],
    ["2017-01-09", 12],
    ["2017-01-16", "Assessment"],
    ["2017-01-23", "Assessment"],
    ["2017-01-30", 1],
    ["2017-03-27", "Vacation"],
    ["2017-04-24", 9],
    ["2017-05-15", 12],
    ["2017-05-22", "Assessment"],
    ["2017-06-12", "Vacation"],

    ## 2017-18
    ["2017-09-04", "Pre Semester 1", 1],
    ["2017-10-02", 1],
    ["2017-12-18", "Vacation"],
    ["2018-01-08", 12],
    ["2018-01-15", "Assessment"],
    ["2018-01-29", 1],
    ["2018-03-19", "Vacation"],
    ["2018-04-16", 8],
    ["2018-05-21", "Assessment"],
    ["2018-06-11", "Vacation"],
    ["2018-08-20", "Resit"],

    ## This is an explicit stop date now at week 52 -- turns out that
    ## consecutive years do not necessarily start and end at the same point.
    ["2018-08-27"]
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
    return [[parse_date(d[0])] + d[1:] for d in cal_config]

def lint_calendar(cal):

    #last_calendar_week = 0
    last_semester_week = 0
    semester = 1
    end_date = None

    for d in cal:
        ## a single date signifies the end of the calendar, so complain if it
        ## does not!
        if(len(d) == 1):
            if(end_date):
                raise Exception("Calendar continues after end date: {}"
                                 .format(d))
            else:
                end_date = d
                continue

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
                raise Exception("Semester Weeks {} and {} are not increasing, at: {}".
                                format(d[1], last_semester_week, d) )
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

    while (working_week):
        ## add the working week
        retn_cal.append(working_week)

        ## clone working week as we are going to change it now
        working_week = list(working_week)

        ## increment the semester week for next time!
        if(type(working_week[1]) is int):
            working_week[1] = working_week[1] + 1

        ## increment the calendar week for next time
        working_week[2] = working_week[2] + 1
        ## work out the date after the current working week
        one_week_ahead = add_week(working_week[0])

        ## remember the calendar week here, because the next config might be shorter
        calendar_week = working_week[2]

        ## if there is a next element left on the calendar config
        ## and it's date is identical, then just use that instead
        if(len(cal_clone)>0 and
           one_week_ahead==cal_clone[0][0]):
            working_week = cal_clone.pop(0)
        else:
            working_week = [one_week_ahead,working_week[1],working_week[2]]

        ## if the new working week is too short, then we need to add a calendar_week
        if(len(working_week)==2):
            working_week.append(calendar_week)

        ## stop!!!
        if(len(working_week)==1):
            working_week = None


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
        summary = "Sem:{} Week:{} Cal:{}".format(semester,e[1],e[2])
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
