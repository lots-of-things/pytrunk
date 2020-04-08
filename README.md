# pytrunk

a simple little python tool to help automate following people on [mastodon](https://joinmastodon.org/). This uses the lists compiled as part of the Mastodon [Trunk](https://communitywiki.org/trunk) project. These are curated lists with people who have signed up as interested in certain topics. Rather than going through manually, this script lets you check who on the lists are still active and how many followers they each have. 

## prerequisites

You need to have selenium set up and working in python3.

```
# Install python dependencies
pip install pytz requests selenium
```

After these dependencies are installed, then you need to install a driver for automated web browsing. Check out [chromedriver's setup page](https://chromedriver.chromium.org/getting-started) for an easy start.

## running the program

first git clone this repository, then perform the following sequence of commands in the terminal.

### 1. save_lists

run `python pytrunk.py save_lists` to download all the available thematic lists from trunk.

### 2. edit your lists

inside lists.json there will be a bunch of list names.  edit the file to remove any that you aren't interested in.

### 3. find_tooters

run `python pytrunk.py find_tooters`. this will step through every list in lists.json and compile some info about each person in there.  it'll check whether they've tooted in the past 30 days, and record the number of followers and follows that they have.  it will also keep track of which lists they are in.  this is stored into tooters.json for use in the next step

### 4. fill out setup.json

there is a json file with details for the last step.  there are three filters MAX_N_FOLLOWERS, MIN_N_FOLLOWERS, MIN_FOLLOWING_OVER_FOLLOWER_RATIO to set.  you also need to set the home domain for your personal mastodon account, and the location of the driver you want to use to load your automated browser (see selenium setup above). 

eg
```
{
    "MAX_N_FOLLOWERS" : 1000,
    "MIN_N_FOLLOWERS" : 10,
    "MIN_FOLLOWING_OVER_FOLLOWER_RATIO" : 0.1,
    "home_domain" : "https://fosstodon.org",
    "webdriver_location": "/location/of/chromedriver"
}
``` 

NOTE: the script only counts followers up to 1000. everyone with more than 1000 is just set to 1000.

### 5. follow_tooters

run `python pytrunk.py follow_tooters`. if everything is set up right, a web browser should pop up on the signin page for your mastodon account.  sign in, and then enter y in the terminal.  then it will iterate through the list of mastodon accounts, displaying the follow button and their profile pictures in the web browser.  in the terminal it will also show the last toot, and what lists they are on.  DONT CLICK FOLLOW. instead type "y" in the terminal if you want to follow, or "n" if you don't. the script will click follow for you and move on to the next person.

### 6. have more friends

you can stop whenever you like.
