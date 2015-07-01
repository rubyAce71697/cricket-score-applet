# -*- coding: utf-8 -*-

import requests

BASE_URL = "http://espncricinfo.com"
SUMMARY_URL = BASE_URL + "/netstorage/summary.json"
MATCH_URL = lambda match_url: BASE_URL + match_url[:-5] + ".json"

class espn_scrap:
    def __init__(self):
        # for maintaing list of matches, an array of "match_info"
        self.match = {}
        """
            "match_info" will contain following fields:

            id                : unique ID of match
            score_summary     : e.g. "Kent - 73/2 (9.2/20 ov) vs Gloucs"
            scorecard_summary : can be empty as only international matches return 'centre' [json data]
            url               : url of match e.g. "http://www.espncricinfo.com/natwest-t20-blast-2015/engine/match/804513.html"
            last_ball         : result of the most recent ball e.g. '1', 'W', '0' etc.
            description       : description of current match e.g. "India tour of Bangladesh, Only Test: Bangladesh v India at Fatullah, Jun 10-14, 2015"
            comms             : live commentary text
            international     : flag for international/domestic matches; True -> international match
        """
        self.dummy_match_info_intl = {
                'id':                ':(',
                'score_summary':     'No data available: check networking settings',
                'scorecard_summary': 'Not available',
                'url':               ':)',
                'last_ball':         '_',
                'description':       'Not available',
                'comms':             'Not available',
                'international':     True,
                }
        self.dummy_match_info_dom = dict(self.dummy_match_info_intl)
        self.dummy_match_info_dom['international'] = False

        # set the parameters which will be sent with each request
        self.requestParam = {
                'Host':            "www.espncricinfo.com",
                'User-Agent':      "Mozilla/5.0 (X11; Linux) Firefox",
                'Accept':          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                'Accept-Encoding': "gzip,deflate",
                'Cookie':          "",
                'Connection':      "keep-alive",
                'Cache-Control':   "max-age=0",
                }

    def get_matches_summary(self):
        try:
            summary = (requests.get(SUMMARY_URL, timeout = 5)).json()
        except Exception as err:
            print ('get_matches_summary: Exception: ', err)
            if self.match == {}:
                return [self.dummy_match_info_intl], [self.dummy_match_info_dom]
            else:
                return [m for m in self.match.values() if m['international']], [m for m in self.match.values() if not m['international']]

        self.match = {}

        intl = []
        for x in summary['modules']['www']:
            if x['category'] == 'intl':
                intl.extend(x['matches'])

        all_matches = summary['matches']
        """
        Data fields returned by summary.json:'matches'
            live_match,     // "Y"/"N" flag
            description,    //info about match
            match_clock,    // time duration from start
            url,            // wrt espncricinfo.com
            result,
            team1_abbrev, team1_name, team1_score,
            team2_abbrev, team2_name, team2_score,
            start_string,   // local + GMT time
            start_time      // date + time of match
        NOTE: incomplete list
        """

        intl_matches = []
        dom_matches = []

        for i in all_matches:
            summary_text = "{team1_abbrev}{team1score} vs {team2_abbrev}{team2score}{startstring}{match_clock}".format(
                team1_abbrev = all_matches[i]['team1_abbrev'].strip().replace('&nbsp;', ' '),
                team1score   = (' - ' + all_matches[i]['team1_score'].strip().replace('&nbsp;', ' ').replace('&amp;', '&'))\
                                if all_matches[i]['team1_score'].strip() else '',
                team2_abbrev = all_matches[i]['team2_abbrev'].strip().replace('&nbsp;',  ' '),
                team2score   = (' - ' + all_matches[i]['team2_score'].strip().replace('&nbsp;', ' ').replace('&amp;', '&'))\
                                if all_matches[i]['team2_score'].strip() else '',
                startstring  = (' at ' + all_matches[i]['start_string'].strip().replace('&nbsp;', ' '))\
                                if 'start_string' in all_matches[i] else '',
                match_clock  = (' in ' + all_matches[i]['match_clock'].strip().replace('&nbsp;', ' '))\
                                if 'match_clock' in all_matches[i] else ''
                )

            match_info = {
                    'id':                i,
                    'score_summary':     summary_text,
                    'scorecard_summary': 'Loading',
                    'url':               all_matches[i]['url'],
                    'last_ball':         "_",
                    'description':       'Loading',
                    'comms':             'Loading',
                    'international':     i in intl
                    }

            self.match[i] = match_info

            if i in intl:
                intl_matches.append(match_info)
            else:
                dom_matches.append(match_info)

        return intl_matches, dom_matches

    def get_match_data(self, m_id):
        try:
            #print (MATCH_URL(self.match[m_id]['url']))
            json_data = (requests.get(MATCH_URL(self.match[m_id]['url']), headers = self.requestParam, timeout = 10)).json()
            #print (json_data)
        except Exception as err:
            print ('get_match_data: Exception: ', err)
            return {}

        self.match[m_id]['last_ball'] = "_"
        if json_data['live']['recent_overs']:
            self.match[m_id]['last_ball'] = (json_data['live']['recent_overs'][-1][-1]['ball']).replace('&bull;', '0')

        """
        split description into parts.
        e.g. "India tour of Bangladesh, Only Test: Bangladesh v India at Fatullah, Jun 10-14, 2015"
        will become:
            India tour of Bangladesh
            Only Test: Bangladesh v India at Fatullah
            Jun 10-14
            2015
        """
        #self.match[m_id]['description'] = '\n'.join(json_data['description'].replace(',', '\n'))
        # HACK: assumes a single space is followed by ','; replace with above line in case of failure
        self.match[m_id]['description'] = json_data['description'].replace(', ', '\n')

        match_summary = "\n" + json_data['live']['status'] + "\n" +\
                              (json_data['live']['break'] + "\n" if json_data['live']['break'] != "" else "")

        # NOTE: there's also json_data['innings'] which is an array of all the innings; 'live':'innings' only tracks the current one
        if json_data['live']['innings']:        # in case match hasn't started yet
            match_summary += "\n{team_name}: {score}/{wickets}   Curr RR: {run_rate}{required_run_rate}".format(\
                                team_name         = [t['team_name'] for t in json_data['team'] if t['team_id'] == json_data['live']['innings']['team_id']][0],
                                score             = json_data['live']['innings']['runs'],
                                wickets           = json_data['live']['innings']['wickets'],
                                run_rate          = json_data['live']['innings']['run_rate'],
                                required_run_rate = "  Required RR: "+json_data['live']['innings']['required_run_rate']\
                                                    if json_data['live']['innings']['required_run_rate'] is not None else ""
                                )

            if json_data['live']['recent_overs']:   # some domestic matches don't have 'recent_overs'
                match_summary += "\nOver (" + json_data['live']['innings']['overs'] + "): " +\
                             " | ".join([ x['ball'].replace('&bull;', '0') +\
                                          x['extras'].replace('&bull;', '0')  for x in json_data['live']['recent_overs'][-1]])
            else:
                match_summary += "\nOvers: " + json_data['live']['innings']['overs']

        if json_data['centre']:     # not available in case of domestic and some international matches, so we cannot rely just on "international" flag
            # NOTE: the formatting work here assumes *monotype* fonts, hence doesn't work for proportionated fonts :(
            # TODO: figure out a better method (tabular?) for displaying this data
            if json_data['centre']['batting']:
                match_summary += "\n\nBatsman:   runs (balls)\n" +\
                                 "\n".join([ " {player_name:<12} {runs:>4} ({balls:^5})".format(\
                                                    # NOTE: in some cases 'popular_name' may be empty, so using 'known_as' instead
                                                    player_name = (x['popular_name'] if x['popular_name'] else x['known_as'])\
                                                                    + ("*" if x['live_current_name'] == "striker" else ""),
                                                    runs        = x['runs'],
                                                    balls       = x['balls_faced']
                                            ) for x in json_data['centre']['batting']])

            if json_data['centre']['bowling']:
                match_summary += "\n\nBowlers:   overs-maidens-runs-wickets  economy-rate\n" +\
                                 "\n".join([ " {player_name:<12} {overs} - {maidens} - {runs} - {wickets}  {economy}".format( \
                                                    player_name = (x['popular_name'] if x['popular_name'] else x['known_as'])\
                                                                    + ("*" if x['live_current_name'] == "current bowler" else ""),
                                                    overs       = x['overs'],
                                                    maidens     = x['maidens'],
                                                    runs        = x['conceded'],
                                                    wickets     = x['wickets'],
                                                    economy     = x['economy_rate']
                                            ) for x in json_data['centre']['bowling']])

        else:
            if json_data['match']['current_summary']:
                # ['match']['current_summary'] is like this:
                #       "Pakistan 58/2 (19.6 ov, Mohammad Hafeez 25*, Younis Khan 1*, KTGD Prasad 2/23)"
                # we need the data inside parenthesis

                t = json_data['match']['current_summary'].split('(')
                t = t[1].split(')')
                t = t[0].split(',')

                match_summary += "\n\nBatsman:   runs\n" +\
                                 "\n".join([ "{player_score_ball}".format(player_score_ball = x)\
                                            for x in t[1:-1]]) +\
                                 "\n\nBowlers:   wickets/runs\n{player_score_ball}".format(player_score_ball = t[-1])

        self.match[m_id]['scorecard_summary'] = match_summary

        self.match[m_id]['comms'] = ""
        if json_data['comms']:
            self.match[m_id]['comms'] = '\n' + '\n'.join(["{overs} {players} : {event}{dismissal}".format(
                                                        overs     = x['overs_actual'],
                                                        players   = x['players'],
                                                        event     = x['event'],
                                                        # HTML character entity references are *evil*
                                                        dismissal = ("\n\t" + x['dismissal'].replace("&amp;","&").replace("&nbsp;"," ").replace("&bull;","0").replace("&dagger;", "(wk)").replace("*", "(c)"))
                                                                    if x['dismissal'] != "" else "",
                                                        ) for x in json_data['comms'][0]['ball'] if 'event' in x])

        return self.match[m_id]
