'''
Created on 06-Jun-2015

@author: nishant
'''


import urllib2
from bs4 import BeautifulSoup
import thread
import time
import signal
import json
import requests


class espn_scrap(object):
    def __init__(self):
        
        #self.match = ""
        self.base_url = "http://www.espncricinfo.com/netstorage/summary.json"
        self.match_component = ""
        #self.match_component_url = "http://www.espncricinfo.com/" + self.match
        self.count = 0
        
        """
            for maintaing list of matches
        """
        
        self.match = []
        self.match_info = {}
        
        
        
        """
            self.match_info = {}
            it will contain following properties:
            
            match_score_summary : 
            {
                eg:
                Kent - 73/2 (9.2/20 ov) vs Gloucs
            }
            
            match_scorecard_summary: 
            {
                can be empty as only international matches return 'centre'
                will be scrapping more later
            }
        
            match_url:
            {
                url is in json
                response is json format
                eg:
                http://www.espncricinfo.com/natwest-t20-blast-2015/engine/match/804513.json
            }

        """
    
    
    
    
    
    def check_scores(self):
        r = requests.get("http://www.espncricinfo.com/netstorage/summary.json")
        r= r.json()
        
        """
            Here the data is scrapped
        """
        self.match = []
        for x in r['matches']:
            ##print r['matches'][x]
            self.string = ""
            self.match_info ={}
            
            self.match_info['match_url'] = r['matches'][x]['url']
            
            #print
            #print str(r['matches'][x]['team1_name']),
            self.string += str(r['matches'][x]['team1_name']).strip().replace('&nbsp;', " ") + " "
            

            if(str(r['matches'][x]['team1_score']).strip()):
                #print "-",
                #print str(r['matches'][x]['team1_score']).strip().replace('&nbsp;', " "),
                self.string += "- " + str(r['matches'][x]['team1_score']).strip().replace('&nbsp;', " ") 
            
            #print "vs",
            self.string += " vs "
            
            #print str(r['matches'][x]['team2_name']).strip(),
            self.string +=  str (r['matches'][x]['team2_name']).strip().replace('&nbsp;', " ") + " "
            

            if(str(r['matches'][x]['team2_score']).strip()):
                #print "-",
                #print str(r['matches'][x]['team2_score']).strip().replace('&nbsp;', " "),
                self.string += "- " + str(r['matches'][x]['team2_score']).strip().replace('&nbsp;', " ")
            ##print " " + r['matches'][x]['start_string'],
            

            if ( 'start_string' in r['matches'][x]):
                #print  "- "+ str(r['matches'][x]['start_string']).replace('&nbsp;', " "),
                self.string += "- " + str(r['matches'][x]['start_string']).strip().replace('&nbsp;', " ")
            

            if( 'start_time' in r['matches'][x]):
                ##print " " + str(r['matches'][x]['start_string']).replace('&nbsp;', " ")
                pass
            self.match_info['match_score_summary'] = self.string
            self.match_info['match_scorecard_summary'] = "Loading"

            self.match.append(self.match_info)
        
        return self.match
    
    def check_match_summary(self,url,count):

        #print
        #print "*"*100


        param= {}
        param['Host'] = "www.espncricinfo.com"
        param['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0"
        param['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        param['Accept-Encoding'] = "gzip,deflate"
        param['Cookie'] = "s_pers=%20s_c24%3D1433087687735%7C1527695687735%3B%20s_c24_s%3DLess%2520than%25201%2520day%7C1433089487735%3B%20s_gpv_pn%3Dcricinfo%253Ahomepage%253Ahomepage%7C1433089487737%3B; _chartbeat2=C6K2flB0OrL0sV_y4.1419663132639.1433087691535.1111111100111111; __unam=7273b75-14a8ca09eb5-29172e7b-10; _cb_ls=1; tscookie=%5B%7B%22mtext%22%3A%22NZ%20%20350%20V%20Eng%20%20253%2F5%22%2C%22mid%22%3A%22743941%22%2C%22mlink%22%3A%22%2Fengland-v-new-zealand-2015%2Fengine%2Fmatch%2F743941.html%22%7D%2C%7B%22mtext%22%3A%22Pak%20%20V%20Zim%20%22%2C%22mid%22%3A%22868731%22%2C%22mlink%22%3A%22%2Fpakistan-zimbabwe-2015%2Fengine%2Fmatch%2F868731.html%22%7D%2C%7B%22mtext%22%3A%22Derbs%20%20V%20Glouc%20%22%2C%22mid%22%3A%22804349%22%2C%22mlink%22%3A%22%2Fcounty-championship-div2-2015%2Fengine%2Fmatch%2F804349.html%22%7D%5D; s_sess=%20s_cc%3Dtrue%3B%20s_sq%3D%3B%20s_omni_lid%3D%3B; bentonLoaded=true"
        param['Connection'] = "keep-alive"
        param['Cache-Control'] = "max-age=0"
        #print "$$$$$$$$$$$$$$$$$$$$"*40
        j = requests.get(url, headers = param)
        #print j
        j = j.json()
        match_summary = ""

        #print count

        ##print self.menu_item_submenu_item[count].get_label()
        #print
        #print "whole information"
        #print
        for x in j:
            #print x ,
            #print j[x]
            pass

        #print
        #print "="*100
        #print

        #print "centre "
        #print

        
        for x in j['centre']:
            #print x + ":",
            #print j['centre'][x]
            pass

        #print "centre fow"
        #print 
        #print
        """

        for x in j['centre']['fow'][0]:
            #print
            #print x + ":",
            #print j['centre']['fow'][0][x]

            if(x == 'player'):
                #print
                for y in j['centre']['fow'][0][x]:
                    #print
                    #print "player "
                    #print y
                    for z in y:
                        #print z + ":",
                        #print y[z]
        """

        #print "centre batting"
        #print 
        #print 
        """
        if('batting' in  j['centre']):
            for x in j['centre']['batting']:
                ##print "player : "+ str(x)
                #print
                for y in x: 
                    #print y + ": ",
                    #print x[y]

                    match_summary += str(y) + ": " + str(x[y])

        """

        #print
        #print j['live']['status']
        match_summary += "\n" + str(j['live']['status'])
        #print j['live']['break']
        match_summary += "\n" + str(j['live']['break']) + "\n"
        
        #print
        #print
        #print "centre batting players"

         
        
        if( 'batting' in j['centre']):
            bat = j['centre']['batting']
            
            match_summary += "\n<b>Batsman\n"
            for x in bat:
                ##print "player : "+ str(x)
                #print
                
                
                """
                for y in x: 
                    #print y + ": ",
                    #print x[y]
                """

                #print "name                  : " + x['popular_name']
                #print "runs                  : " + x['runs']
                #print "balls                 : " + x['balls_faced']
                #print "striker/non-striker   : " + x['live_current_name']
                #print "out/not out           : " + x['dismissal_name']

                

                match_summary +=  "\n" + "name                                   : " + str(x['popular_name'])
                if(x['live_current_name'] == "striker"):
                    match_summary += "*"
                match_summary +=  "\n" + "runs                                      : " + str(x['runs'])
                match_summary +=  "\n" + "balls                                     : " + str(x['balls_faced'])
                #match_summary +=  "\n" + "striker/non-striker      : " + str(x['live_current_name'])
                match_summary +=  "\n" + "out/not out                     : " + str(x['dismissal_name'])
                match_summary += "\n"
        #print
        #print
        #print "centre bowling players"
         
        if ('bowling' in j['centre']):
            match_summary += "\n\nBowlers\n"
            bat = j['centre']['bowling']
            ##print bat
            for x in bat:
                ##print "player : "+ str(x)
                #print
                """
                for y in x: 
                    #print y + ": ",
                    #print x[y]
                """

                #print "name               : " + str(x['popular_name'])
                #print "wickets            : " + str(x['wickets'])
                #print "runs conceded      : " + str(x['conceded'])
                #print "overs bowled       : " + str(x['overs'])
                #print "maiden overs       : " + str(x['maidens'])
                #print "current/previous   : " + str(x['live_current_name'])
                #print "economy rate       : " + str(x['economy_rate'])



                match_summary += "\n" + "name                                  : " + str(x['popular_name'])
                if x['live_current_name'] == 'current bowler':
                    match_summary += "*"
                match_summary += "\n" + "wickets                             : " + str(x['wickets'])
                match_summary += "\n" + "runs conceded              : " + str(x['conceded'])
                match_summary += "\n" + "overs bowled                : " + str(x['overs'])
                match_summary += "\n" + "maiden overs               : " + str(x['maidens'])
                #match_summary += "\n" + "current/previous   : " + str(x['live_current_name'])
                match_summary += "\n" + "economy rate               : " + str(x['economy_rate'])
                match_summary += "\n"
        #print "count :" + str(count)        

        #print j['live']['status']
        #print "+"*100
        self.match[count]['match_scorecard_summary'] = match_summary

        return self.match[count]        

        

