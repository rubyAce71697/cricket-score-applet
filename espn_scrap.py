"""
Created on 06-Jun-2015

@author: nishant
"""

import requests
import re

SUMMARY_URL = "http://www.espncricinfo.com/netstorage/summary.json"

class espn_scrap:
    def __init__(self):
        # for maintaing list of matches
        match_info = {}
        """
            TODO: Update the new fields

            "match_info" will contain following properties:

            match_score_summary {
                eg: "Kent - 73/2 (9.2/20 ov) vs Gloucs"
            }

            match_scorecard_summary {
                can be empty as only international matches return 'centre'
                will be scrapping more later
            }

            match_url {
                url is of json
                response is json format
                eg: "http://www.espncricinfo.com/natwest-t20-blast-2015/engine/match/804513.json"
            }
        """
        self.dummy_match_info = {
                'match_score_summary': 'No data available: check networking settings',
                'match_description': 'No description available',
                'match_ball' : "No description available",
                'match_scorecard_summary': 'No summary available',
                'match_url': 'http://127.0.0.1',
                }

        # set the parameters which will be sent with each request
        self.requestParam = {}
        self.requestParam['Host'] = "www.espncricinfo.com"
        self.requestParam['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux) Firefox"
        self.requestParam['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        self.requestParam['Accept-Encoding'] = "gzip,deflate"
        self.requestParam['Cookie'] = ""
        self.requestParam['Connection'] = "keep-alive"
        self.requestParam['Cache-Control'] = "max-age=0"

        """
        Data fields returned by JSON:
            live_match,     // boolean flag
            description,    //info about match
            match_ball,
            match_clock,    // time duration from start
            url,
            result,
            team1_abbrev, team1_name, team1_score,
            team2_abbrev, team2_name, team2_score,
            start_string,   // local + GMT time
            start_time      // data + time
        NOTE: incomplete list
        """

    def get_matches_summary(self):
        try:
            all_matches = (requests.get(SUMMARY_URL)).json()['matches']
        except Exception as err:
            print ('Exception: ', err)
            return [self.dummy_match_info]

        # Here the data is scrapped
        self.match = []
        for i in all_matches:
            # TODO: consider using match_clock if startstring is not available
            summary_text = "{team1}{team1score} vs {team2}{team2score} {startstring}".format(
                    team1       = all_matches[i]['team1_name'].strip().replace('&nbsp;', " "),
                    team1score  = (" - " + all_matches[i]['team1_score'].strip().replace('&nbsp;', " ").replace('&amp;', '&')) if all_matches[i]['team1_score'].strip() else "",
                    team2       = all_matches[i]['team2_name'].strip().replace('&nbsp;', " "),
                    team2score  = (" - " + all_matches[i]['team2_score'].strip().replace('&nbsp;', " ").replace('&amp;', '&')) if all_matches[i]['team2_score'].strip() else "",
                    startstring = (" - " + str(all_matches[i]['start_string']).strip().replace('&nbsp;', " ")) if 'start_string' in all_matches[i] else ""
                    )

            
            match_info = {
                    'match_url':               all_matches[i]['url'],
                    
                    'match_score_summary':     summary_text,
                    'match_scorecard_summary': "Loading"
                    }

            self.match.append(match_info)
            """
            print "in get matches summary"
            for s in self.match:
                print s
            """
        return self.match

    def check_match_summary(self, url, count):
        try:
            json_data = (requests.get(url, headers = self.requestParam)).json()
        except Exception as err:
            print ('Exception: ', err)
            return self.dummy_match_info

        match_summary = ""

        for x in json_data:
            pass

        for x in json_data['centre']:
            pass

        self.match[count]['match_ball'] = ""
        if(json_data['live']['recent_overs']):
            self.match[count]['match_ball'] = json_data['live']['recent_overs'][-1][-1]['ball']

        #print "in espn_scrap : " + str(count) + " : " +  json_data['live']['recent_overs'][-1][-1]['ball']
        """
        self.match[count]['description'] = json_data['description']
        """
        self.match[count]['description'] = ""
        for x in json_data['description'].split(','):
            #print x
            
            if(len(x) >= 44):
                for y in x.split(':'):
                    self.match[count]['description'] += y.lstrip() + "\n"
                self.match[count]['description'] = self.match[count]['description'][:-1]

            else:
                self.match[count]['description'] += x.lstrip()


            self.match[count]['description'] += "\n"
        
        self.match[count]['description'] = self.match[count]['description'][:-1]
        

        """
            get status and break information
        """

        match_summary += "\n" + str(json_data['live']['status'])
        match_summary += "\n" + str(json_data['live']['break']) + "\n"


        if(json_data['live']['recent_overs']):
            match_summary += "\nOver "
            match_summary += "("+ str(json_data['match']['live_overs_unique']).replace(".0",".") + ") : "

            for x in json_data['live']['recent_overs'][-1]:
                match_summary += x['ball'].replace('&bull;', '0')
                match_summary += x['extras'].replace('&bull;', '0')
                match_summary += "|"
            

        if(json_data['centre']):
            if( 'batting' in json_data['centre']):
                match_summary += "\n\n"
                
                bat = json_data['centre']['batting']

                match_summary += "Batsman   runs(balls)\n"
                for x in bat:
                    
                    match_summary +=  str(x['popular_name'])
                    if(x['live_current_name'] == "striker"):
                        match_summary += "*"
                    match_summary += "  "
                    match_summary += str(x['runs'])
                    match_summary += "("
                    match_summary += str(x['balls_faced'])
                    match_summary += ")"
                    match_summary += "     "



            
            if ('bowling' in json_data['centre']):
                match_summary += "\n\nBowlers:   overs-madeins-runs-wickets   economy-rate"
                bat = json_data['centre']['bowling']
                for x in bat:
                    
                    match_summary += "\n" +  str(x['popular_name'])
                    if x['live_current_name'] == 'current bowler':
                        match_summary += "*"
                    match_summary += " : "
                    match_summary +=  str(x['overs']) + "-"
                    match_summary +=  str(x['maidens']) + "-"
                    match_summary +=  str(x['conceded']) + "-"
                    match_summary +=  str(x['wickets']) 
                    match_summary += "    Econ: " + str(x['economy_rate'])
                    
                    
                    
                    
                    #match_summary += "\n" + "current/previous   : " + str(x['live_current_name'])
                    
                    match_summary += "\n"

            

        print json_data['comms']
        self.match[count]['comms'] = ""
        match_comm = ""
        for x in json_data['comms'][0]['ball']:
            if ('event' in x):
                
                
                
                if ('event' in x):
                    if(x['event'] == "OUT"):
                        x['dismissal'] = " : " + x['dismissal']
                        pass
                    if(x['text']):
                        x['text'] = " : " + x['text']
                        if( len(x['text']) >= 44 ):
                            t = x['text'].split(",")
                            x['text'] = ""
                            x['text'] += t[0]
                            x['text'] += "\n"
                            x['text'] += t[1].lstrip()
                
                #print 'commentary'
                #print x['overs_actual'] + " "  + x['players'] + " : " + " " +  x['event'] + x['dismissal']  +x['text']
                match_comm += (x['overs_actual'] + " "  + x['players'] + " : " + " " +  x['event'] + x['dismissal']  +x['text']).rstrip()
                match_comm += '\n'
            



        self.match[count]['comms'] = match_comm
    
        #self.match[count]['comms'] = json_data['comms']

        self.match[count]['match_scorecard_summary'] = match_summary
        print "in espn_scrap"
        print self.match[count]['description']

        
        print self.match[count]
        
        print self.match[count]['description']
        print "in espn_scrap"
        print self.match[count].keys()
        print self.match[count]
        return self.match[count]
