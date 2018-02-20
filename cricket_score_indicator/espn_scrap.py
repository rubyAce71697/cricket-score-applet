# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import requests

BASE_URL = "http://api.espncricinfo.com"
#BASE_URL = "http://fcast.us-west-2.espncdn.com"



SUMMARY_URL = BASE_URL + "/netstorage/summary.json"
#SUMMARY_URL = BASE_URL + "/FastcastService/pubsub/profiles/12000/topic/event-topevents-espncricinfo-in-en/message/253105/checkpoint"
# remove `html' and add `json'
MATCH_URL_JSON = lambda match_url: BASE_URL + match_url[:-4] + "json"
MATCH_URL_HTML = lambda match_url: BASE_URL + match_url

# parameters which will be sent with each request
REQUEST_PARAM = {
        'Host':            "www.espncricinfo.com",
        'User-Agent':      "Mozilla/5.0 (X11; Linux) Firefox",
        'Accept':          "text/html;q=0.9,*/*;q=0.8",
        'Accept-Encoding': "gzip,deflate",
        'Cookie':          "",
        'Connection':      "keep-alive",
        'Cache-Control':   "max-age=0",
    }
DEFAULT_ICON = "default"

"""
match_info is the dict returned by both functions.
    "match_info" will contain following fields:
    id                : unique ID of match
    url               : url of match e.g. "http://www.espncricinfo.com/natwest-t20-blast-2015/engine/match/804513.html"
    scoreline         : e.g. "Kent - 73/2 (9.2/20 ov) vs Gloucs"
    scorecard         : can be empty as only international matches return 'centre' [json data]
    description       : description of current match e.g. "India tour of Bangladesh, Only Test: Bangladesh v India at Fatullah, Jun 10-14, 2015"
    comms             : live commentary text
    last_ball         : result of the most recent ball e.g. '1', 'W', '0' etc.
    intl              : flag for international/domestic matches; True -> international match
    status            : status of the match e.g. Innings break, Day2-Session 1 etc.
"""

def get_matches_summary():
    """
        returns a 2-tuple of lists containing match_info of intl [0] and domestic [1] matches
    """

    # we'll return these two lists
    intl_matches = []
    dom_matches = []

    try:
        summary = (requests.get(SUMMARY_URL, timeout=5)).json()
    except Exception as err:
        print ('get_matches_summary: Exception: ', err, file=sys.stderr)
        return None, None

    # save the id of intl matches; we'll use it for flagging individual matches
    intl = []
    # summary['modules']['www'] is a list of dicts
    # each dict has 2 keys of interest: category(str), matches(list)
    # we look for items with 'intl' category
    for x in summary['modules']['www']:     # 'www' == international version of website
        if x['category'] == 'intl':
            intl.extend(x['matches'])

    # Data fields in a summary['matches'] (dict) item
    #     live_match,     // "Y"/"N" flag
    #     description,    //info about match
    #     match_clock,    // time duration from start
    #     url,            // wrt espncricinfo.com
    #     result,
    #     team1_abbrev, team1_name, team1_score,
    #     team2_abbrev, team2_name, team2_score,
    #     start_string,   // local + GMT time
    #     start_time      // date + time of match
    # NOTE: incomplete list

    # iterate over the match ids
    for m_id, m_val in summary['matches'].iteritems():
        # create the summaryline
        summaryline = "{team1_abbrev}{team1score} vs {team2_abbrev}{team2score}{startstring}{match_clock}".format(
            team1_abbrev = m_val['team1_abbrev'].strip().replace('&nbsp;', ' '),
            team1score   = (' - ' + m_val['team1_score'].strip().replace('&nbsp;', ' ').replace('&amp;', '&'))\
                            if m_val['team1_score'].strip() else '',
            team2_abbrev = m_val['team2_abbrev'].strip().replace('&nbsp;', ' '),
            team2score   = (' - ' + m_val['team2_score'].strip().replace('&nbsp;', ' ').replace('&amp;', '&'))\
                            if m_val['team2_score'].strip() else '',
            startstring  = (' at ' + m_val['start_string'].strip().replace('&nbsp;', ' '))\
                            if 'start_string' in m_val else '',
            match_clock  = (' in ' + m_val['match_clock'].strip().replace('&nbsp;', ' '))\
                            if 'match_clock' in m_val else ''
            )

        match_info = {
                'id'                :           m_id,
                'url'               :           m_val['url'],
                'scoreline'         :           summaryline,
                'scorecard'         :           "Loading",
                'description'       :           "Loading",
                'comms'             :           "",
                'last_ball'         :           DEFAULT_ICON,
                'intl'              :           m_id in intl,
                'status'            :           "",
                'label_scoreline'   :           ""
                }
        if m_id in intl:
            intl_matches.append(match_info)
        else:
            dom_matches.append(match_info)
    
    return intl_matches, dom_matches

def get_match_data(match_url):
    """
    returns detailed match data (match_info) for `match_url`
    """

    try:
        #print match_url
        json_data = (requests.get(MATCH_URL_JSON(match_url), headers=REQUEST_PARAM, timeout=10)).json()
    except Exception as err:
        print ('get_match_data: Exception: ', err, file=sys.stderr)
        return None

    match = {}
    ### setting 'description'
    """
    split description into parts.
    e.g. "India tour of Bangladesh, Only Test: Bangladesh v India at Fatullah, Jun 10-14, 2015"
    will become:
        India tour of Bangladesh
        Only Test: Bangladesh v India at Fatullah
        Jun 10-14
        2015
    """
    # match['description'] = '\n'.join(json_data['description'].replace(',', '\n'))
    # HACK: assumes a single space is followed by ','; replace with above line in case of failure
    match['description'] = json_data['description'].replace(', ', '\n')

    ########################################

    ### setting status for match

    status =  json_data['live']['break'] + "\n" if json_data['live']['break'] != "" else ""

    match['status'] = status
    print (match['status'])




    match['label_scoreline'] = ""

    ########################################


    ### setting 'scorecard'
    scorecard = json_data['live']['status'] + "\n" +\
                          (json_data['live']['break'] + "\n" if json_data['live']['break'] != "" else "")

    # 'score and RR' line

    print (json_data['live']['innings'])
    if json_data['live']['innings']:
        print (json_data['live']['innings'])

        ### 'setting shortlabel'
        shortlabel = "{team_name}: {score}/{wickets} Over ({over})".format(\
                                team_name   = [t['team_abbreviation'].strip() for t in json_data['team'] if t['team_id'] == json_data['live']['innings']['team_id']][0],
                                score       = json_data['live']['innings']['runs'],
                                wickets     = json_data['live']['innings']['wickets'],
                                over        = json_data['live']['innings']['overs'],

                                )
        match['label_scoreline'] = shortlabel


        # NOTE: there's also json_data['innings'] which is an array of all the innings; 'live':'innings' only tracks the current one
        scorecard += "\n{team_name}: {score}/{wickets}   Curr RR: {run_rate}{required_run_rate}".format(\
                            team_name         = [t['team_name'] for t in json_data['team'] if t['team_id'] == json_data['live']['innings']['team_id']][0],
                            score             = json_data['live']['innings']['runs'],
                            wickets           = json_data['live']['innings']['wickets'],
                            run_rate          = json_data['live']['innings']['run_rate'],
                            required_run_rate = "  Required RR: "+json_data['live']['innings']['required_run_rate']\
                                                if json_data['live']['innings']['required_run_rate'] is not None else ""
                            )

        if json_data['live']['recent_overs']:   # some domestic matches don't have 'recent_overs'
            scorecard += "\nOver (" + json_data['live']['innings']['overs'] + "): " +\
                         u" • ".join([ x['ball'].replace('&bull;', '0') +\
                                      x['extras'].replace('&bull;', '0')  for x in json_data['live']['recent_overs'][-1]])
        else:
            scorecard += "\nOvers: " + json_data['live']['innings']['overs']

    # 'Last Wicket' line
    if json_data['live']['fow']:
        for item in json_data['live']['fow']:
            if item['live_current_name'] == 'last wicket' and item['player_id'] is not None:    # player info is not available in some domestic matches, hence we check before use
                player_name = "<null>"

                for team in json_data['team']:
                    if team['team_id'] == item['team_id']:
                        for player in team['player']:
                            if player['player_id'] == item['player_id']:
                                player_name = player['known_as']        # NOTE: there are multiple "names", check which one is suitable
                                break
                        break

                scorecard += "\n\nLast Wicket: {player_name} {runs}({balls}) {dismissal_string}".format(\
                                    player_name      = player_name,
                                    runs             = item['out_player']['runs'],
                                    balls            = item['out_player']['balls_faced'],
                                    dismissal_string = item['out_player']['dismissal_string'].
                                    			replace("&amp;", "&").
                                    			replace("&nbsp;", " ").
                                    			replace("&bull;", "0").
                                    			replace("&dagger;", "(wk)").
                                    			replace("*", "(c)")
                                )
                break

    # 'Batsman' and 'Bowlers' lines
    if json_data['centre']:     # not available in case of domestic and some international matches, so we cannot rely just on "international" flag
        # NOTE: the formatting work here assumes *monotype* fonts, hence doesn't work for proportionated fonts :(
        # TODO: figure out a better method (tabular?) for displaying this data
        if json_data['centre']['batting']:
            scorecard += "\n\nBatsman:   runs (balls)\n" +\
                             "\n".join(" {player_name:<12} {runs:>4} ({balls:^5})".format(\
                                                # NOTE: in some cases 'popular_name' may be empty, so using 'known_as' instead
                                                player_name = (x['popular_name'] if x['popular_name'] else x['known_as'])\
                                                                + ("*" if x['live_current_name'] == "striker" else ""),
                                                runs        = x['runs'],
                                                balls       = x['balls_faced']
                                        ) for x in json_data['centre']['batting'])

        if json_data['centre']['bowling']:
            scorecard += "\n\nBowlers:   overs-maidens-runs-wickets  economy-rate\n" +\
                             "\n".join(" {player_name:<12} {overs} - {maidens} - {runs} - {wickets}  {economy}".format( \
                                                player_name = (x['popular_name'] if x['popular_name'] else x['known_as'])\
                                                                + ("*" if x['live_current_name'] == "current bowler" else ""),
                                                overs       = x['overs'],
                                                maidens     = x['maidens'],
                                                runs        = x['conceded'],
                                                wickets     = x['wickets'],
                                                economy     = x['economy_rate']
                                        ) for x in json_data['centre']['bowling'])

    else:
        if 'current_summary' in json_data['match'] and json_data['match']['current_summary']:
            # ['match']['current_summary'] is like this:
            #       "Pakistan 58/2 (19.6 ov, Mohammad Hafeez 25*, Younis Khan 1*, KTGD Prasad 2/23)"
            # we need the data inside parenthesis

            t = json_data['match']['current_summary'].split('(')
            if len(t) == 2:
                # we got a clean split
                t = t[1].split(')')
                t = t[0].split(',')

                scorecard += "\n\nBatsman:   runs\n" +\
                                 "\n".join("{player_score_ball}".format(player_score_ball=x)\
                                            for x in t[1:-1]) +\
                                 "\n\nBowlers:   wickets/runs\n{player_score_ball}".format(player_score_ball=t[-1])

    # cat all to form the scoreboard
    match['scorecard'] = scorecard

    ########################################

    ### setting 'last_ball'
    if 'won by' in match['scorecard'] or 'drawn' in match['scorecard']:
        match['last_ball'] = "V"
    elif json_data['live']['recent_overs']:
        match['last_ball'] = (json_data['live']['recent_overs'][-1][-1]['ball']).replace('&bull;', '0')[0]
    else:
        match['last_ball'] = DEFAULT_ICON

    ########################################

    # setting 'comms'
    match['comms'] = ""
    if json_data['comms']:
        match['comms'] = '\n'.join("{overs} {players} : {event}{dismissal}".format(
                                                    overs     = x['overs_actual'],
                                                    players   = x['players'],
                                                    event     = x['event'],
                                                    # HTML character entity references are *evil*
                                                    dismissal = ("\n\t" + x['dismissal'].replace("&amp;","&").replace("&nbsp;"," ").replace("&bull;","0").replace("&dagger;", "(wk)").replace("*", "(c)"))
                                                                if x['dismissal'] != "" else "",
                                                    ) for x in json_data['comms'][0]['ball'] if 'event' in x)

    #print str(match)
    return match
