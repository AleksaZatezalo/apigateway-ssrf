"""
Author: Aleksa Zatezalo
Date: March 2025
Description: A remote code execution exploit that leverages SSRF on the Kong API gateway.
"""

def log(message):
    """
    Prints a string, message, to standard output.
    """

    pass

def parseAPIKeyResponse(response):
    """
    Parses response from Kong API Gateway to get Admin Panel API key.
    """

    pass

def getAPIKey(url):
    """
    Leverages SSRF on Kong API gateway found at URL return API key for admin panel.
    """

    pass

def checkPlugins(url, apikey):
    """
    Checks Kong Admin Panel to see if a plugin supporting RCE is enabled on the Admin panel.
    """
    
    pass

def makeShell(lhost, lport):
    """
    Returns a lua revshell for lhost and lport.
    """

    pass

def formatHTML(lhost, lport):
    """
    Formats HTML RCE code.
    """

    pass

def starServer(lport, lhost):
    """
    Starts apache server and moves HTML payload to server.
    """

    pass

def createPlugin(url, lport, lhost):
    """
    Sends a request to get the proper plugin.
    """

    pass

def getRCE(url):
    """
    Self explanitory.
    """

    pass