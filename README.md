# minerva2gcal
*A tool to download calendars from Minerva Medicine (the VLE learning system
used at University of Sheffield Medical School), convert it into an appropriate
format for Google Calendar and import it*

## Using minerva2gcal
If it's the first time, run `first_run.py`

On future runs, run `google_import.py`

It's intended to be run on a dedicated calendar, because **THIS WILL DELETE THE
EVENTS ON THE CALENDAR** before then adding it's own on to it. This is because
the Minerva calendar is often changed, and events are renamed. With no way to
track these changes and detect renames/deletions, we have to start from scratch
on each run

## Configuring rejections
This is a setting that can be changed to exclude events by specifying a list of
regular expressions that are matched against event descriptions

e.g.
```
REJECTS = [
    'travel\/private study',
    'Self Directed Learning',
    'ILA groups (24-30|1-8|9-16)',
    'Personal\/Self directed study',
    'Early Years .* Class B',
    'Prescribing Session',
    'Prescribing Answers Session',
    'Travel Time',
    'Dedicated Free Time',
    'Microbiology practical.*Class B',
    'Personal\/Private study time',
    'Easter Vaccation',
    'Reading week',
]
```

## Caveats
1. The calendar is cleared before upload
2. When looping over the events, we still have to go over each pages of deleted
events, since events on Google Calendar go in the bin. At the time of writing,
there is no way to empty the trash from API. This means that the tool takes
longer and longer to complete each time, until the deleted events are cleared
after 30 days of being in the trash
3. The tool needs to be run a couple of times a week during term time, since
events are added/changed/deleted on Minerva, often on short notice
