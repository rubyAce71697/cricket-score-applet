"""
Created on 06-Jun-2015

@author: nishant
"""

import requests

BASE_URL = "http://www.espncricinfo.com"
SUMMARY_URL = BASE_URL + "/netstorage/summary.json"
MATCH_URL = lambda match_url: BASE_URL + match_url[:-5] + ".json"

class espn_scrap:
    def __init__(self):
        self.offline = True

        # for maintaing list of matches, an array of "match_info"
        self.match = []
        """
            "match_info" will contain following fields:

            score_summary:
                e.g. "Kent - 73/2 (9.2/20 ov) vs Gloucs"

            scorecard_summary:
                can be empty as only international matches return 'centre' [json data]

            url:
                url of match
                e.g. "http://www.espncricinfo.com/natwest-t20-blast-2015/engine/match/804513.html"

            ball:
                result of the most recent ball
                e.g. '1', 'W', '0' etc.

            description:
                description of current match
                e.g. "India tour of Bangladesh, Only Test: Bangladesh v India at Fatullah, Jun 10-14, 2015"

            comms:
                live commentary text
                TODO

            international:
                flag for international/domestic matches; == 1 -> international match

        """
        self.dummy_match_info = {
                'score_summary':     'No data available: check networking settings',
                'scorecard_summary': 'Not available',
                'url':               'http://0.0.0.0',
                'ball':              'Not available',
                'description':       'Not available',
                'comms':             'Not available',
                'international':     'Not available',
                }

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

        """
        Data fields returned by summary.json:
            live_match,     // "Y"/"N" flag
            description,    //info about match
            match_clock,    // time duration from start
            url,            // wrt espncricinfo.com
            result,
            team1_abbrev, team1_name, team1_score,
            team2_abbrev, team2_name, team2_score,
            start_string,   // local + GMT time
            start_time      // data + time
        NOTE: incomplete list
        """

    def is_offline(self):
        return self.offline

    def get_matches_summary(self):
        try:
            summary = (requests.get(SUMMARY_URL)).json()
        except Exception as err:
            print ('Exception: ', err)
            self.offline = True
            if self.match == []:
                return [self.dummy_match_info]
            else:
                return self.match

        self.offline = False
        self.match = []
        # NOTE: if get_match_data is called at this point, then we're in trouble

        intl = []
        for x in summary['modules']['www']:
            if x['category'] == 'intl':
                intl.extend(x['matches'])

        all_matches = summary['matches']

        for i in all_matches:
            # TODO: consider using match_clock if startstring is not available
            summary_text = "{team1_abbrev}{team1score} vs {team2_abbrev}{team2score} {startstring}".format(
                team1_abbrev = all_matches[i]['team1_abbrev'].strip().replace('&nbsp;', ' '),
                team1score   = (' - ' + all_matches[i]['team1_score'].strip().replace('&nbsp;', ' ').replace('&amp;', '&'))\
                                if all_matches[i]['team1_score'].strip() else '',
                team2_abbrev = all_matches[i]['team2_abbrev'].strip().replace('&nbsp;',  ' '),
                team2score   = (' - ' + all_matches[i]['team2_score'].strip().replace('&nbsp;', ' ').replace('&amp;', '&'))\
                                if all_matches[i]['team2_score'].strip() else '',
                startstring  = (' - ' + all_matches[i]['start_string'].strip().replace('&nbsp;', ' '))\
                                if 'start_string' in all_matches[i] else ''
                )

            match_info = {
                    'score_summary':     summary_text,
                    'scorecard_summary': 'Loading',
                    'url':               all_matches[i]['url'],
                    'ball':              "",
                    'description':       'Loading',
                    'comms':             'Loading',
                    'international':     i in intl
                    }

            self.match.append(match_info)

        return self.match

    def get_match_data(self, index):
        try:
            json_data = (requests.get(MATCH_URL(self.match[index]['url']), headers = self.requestParam)).json()
        except Exception as err:
            print ('Exception: ', err)
            self.offline = True
            if self.match == [] or len(self.match) < index:
                return self.dummy_match_info
            else:
                return self.match[index]

        self.offline = False

        self.match[index]['ball'] = ''
        if json_data['live']['recent_overs']:
            self.match[index]['ball'] = (json_data['live']['recent_overs'][-1][-1]['ball']).replace('&bull;', '0')

        """
        split description into parts.
        e.g. "India tour of Bangladesh, Only Test: Bangladesh v India at Fatullah, Jun 10-14, 2015"
        will become:
            India tour of Bangladesh
            Only Test: Bangladesh v India at Fatullah
            Jun 10-14
            2015
        """
        #self.match[index]['description'] = '\n'.join(json_data['description'].replace(',', '\n'))
        # HACK: assumes a single space is followed by ','; replace if above line in case of failure
        self.match[index]['description'] = json_data['description'].replace(', ', '\n')

        match_summary = "\n" + json_data['live']['status'] + "\n" +\
                              (json_data['live']['break'] + "\n" if json_data['live']['break'] != "" else "")

        # NOTE: there's also json_data['innings'] which is an array of all the innings; 'live':'innings' only tracks the current one
        if json_data['live']['innings']:        # in case match hasn't started yet
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
                                 "\n".join([ "{player_name:<12} {runs:>4} ({balls:^5})".format( \
                                                    player_name = x['popular_name'] + ("*" if x['live_current_name'] == "striker" else ""),
                                                    runs        = x['runs'],
                                                    balls       = x['balls_faced']
                                            ) for x in json_data['centre']['batting']])

            if json_data['centre']['bowling']:
                match_summary += "\n\nBowlers:   overs-maidens-runs-wickets  economy-rate\n" +\
                                 "\n".join([ "{player_name:<12} {overs} - {maidens} - {runs} - {wickets}  {economy}".format( \
                                                    player_name = x['popular_name'] + ("*" if x['live_current_name'] == "current bowler" else ""),
                                                    overs       = x['overs'],
                                                    maidens     = x['maidens'],
                                                    runs        = x['conceded'],
                                                    wickets     = x['wickets'],
                                                    economy     = x['economy_rate']
                                            ) for x in json_data['centre']['bowling']])

        self.match[index]['scorecard_summary'] = match_summary

        self.match[index]['comms'] = ""
        # NOTE: 'comms' field is not available in domestic matches, check before use
        #match_comm = ""
        #for x in json_data['comms'][0]['ball']:
        #    if ('event' in x):
        #        if(x['event'] == "OUT"):
        #            x['dismissal'] = " : " + x['dismissal']
        #            pass
        #        if(x['text']):
        #            x['text'] = " : " + x['text']
        #            if( len(x['text']) >= 44 ):
        #                t = x['text'].split(",")
        #                x['text'] = ""
        #                x['text'] += t[0]
        #                x['text'] += "\n"
        #                x['text'] += t[1].lstrip()

        #        #print 'commentary'
        #        #print x['overs_actual'] + " "  + x['players'] + " : " + " " +  x['event'] + x['dismissal']  +x['text']
        #        match_comm += (x['overs_actual'] + " "  + x['players'] + " : " + " " +  x['event'] + x['dismissal']  +x['text']).rstrip()
        #        match_comm += '\n'

        #self.match[index]['comms'] = match_comm

        return self.match[index]
