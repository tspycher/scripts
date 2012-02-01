import urllib2
import re
import xml.dom.minidom
import sys

class SVN2Mite(object):
    
    __baseUrl = str()
    
    __apiKey = str()
    
    def __init__(self, apiKey, baseUrl):
        self.__apiKey = apiKey
        self.__baseUrl = baseUrl
    
    def hook(self, repository, author, message):
        minutes = 0.0
        
        # get time element
        regex = "(?<=@)[0-9 ].*"
        regexTime = re.compile(regex)
        matchTime = regexTime.search(message)
        if not matchTime: return False
        
        time = matchTime.group()
        
        if not time: return False
        # matches decimal
        regex = "[0-9]{1,}\.[0-9]{1,}"
        regexTimeDecimal = re.compile(regex)
        matchTimeDecimal = regexTimeDecimal.search(time)
        
        if matchTimeDecimal:
            timeDecimal = matchTimeDecimal.group()
            minutes = float(timeDecimal) * 60.0
        else:
            # matches literal
            regex = "[0-9]{1,}(?=h)|[0-9]{1,}(?=m)"
            regexTimeLiteral = re.compile(regex)
            matchTimeLiteral = regexTimeLiteral.findall(time)
            if len(matchTimeLiteral) == 1:
                minutes = float(matchTimeLiteral[0]) * 60.0
            elif len(matchTimeLiteral) >= 2:
                minutes = float(matchTimeLiteral[0]) * 60.0 + float(matchTimeLiteral[1])
        
        print "Minutes: %0.2f" % minutes
        if not minutes:
            return False
        
        # We got the minutes, now get the needed elements
        userId = int(self.getUserId(author))
        projectId = int(self.getProjectId(repository))
        serviceId = int(self.getServiceId('svn'))
        
        print "Got user: %i project: %i and service: %i" % (userId, projectId, serviceId)
        self.addTime(minutes, message, userId, projectId, serviceId)
        
        return True
        
    def getUserId(self, name):
        values = dict()
        self.__i(self.__request('/users.xml?name=%s' % name),values)
        if "id" in values:
            return values['id']
        return 0
        
    def getProjectId(self, name):
        values = dict()
        self.__i(self.__request('/projects.xml?name=%s' % name),values)
        if "id" in values:
            return values['id']
        return 0
    
    def getServiceId(self, name):
        values = dict()
        self.__i(self.__request('/services.xml?name=%s' % name),values)
        if "id" in values:
            return values['id']
        return 0
    
    def addTime(self, minutes, description, userId, projectId, serviceId):
        request = """<time-entry>
        <minutes>%i</minutes>
        <note>%s</note>
        <service-id>%i</service-id>
        <project-id>%i</project-id>
        <user-id>%i</user-id>
        </time-entry>""" % (minutes, description, userId, projectId, serviceId)
        
        self.__request('/time_entries.xml', request)
    
    ## Performs an request
    #  @param url the requested resource eg. /api/customer/view/1.xml realtive to self.__baseUrl
    #  @param body if needed the body for the request. if Set, request method gets automatically set to POST
    #  @return mixed either Boolean or xml.dom.minidom.Document   
    def __request(self, url, body = None):
        response = None
        request = urllib2.Request(self.__baseUrl+url)

        # Header Stuff
        request.add_header("Content-Type", "application/xml")
        request.add_header('X-MiteApiKey', self.__apiKey)

        if body: request.add_data(body)
        
        # perform the request
        try:
            response = urllib2.urlopen(request)
        except urllib2.HTTPError as (code):
            print "Got Error %s" % str(code)
            return False
        
        if response:
            responseData = response.read()
            try:
                self.__xmlResponse = xml.dom.minidom.parseString(responseData)
                return self.__xmlResponse
            except:
                return responseData
        else:
            return True

    def __i(self, doc, values = None):
        for n in doc.childNodes:
            
            if not n.nodeType == n.TEXT_NODE: 
                var = n.nodeName
                val = str()
                if n.childNodes.item(0): val = str(n.childNodes.item(0).nodeValue)
                values[var] = val
                
            if len(n.childNodes): 
                self.__i(n,values)
        
        return values

if __name__ == '__main__':
    mite = SVN2Mite(sys.argv[1], sys.argv[2])
    mite.hook(sys.argv[3], sys.argv[4], sys.argv[5])