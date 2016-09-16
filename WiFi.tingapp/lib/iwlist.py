import re
import subprocess

cellNumberRe = re.compile(r"^Cell\s+(?P<cellnumber>.+)\s+-\s+Address:\s(?P<mac>.+)$")
regexps = [
    re.compile(r"^ESSID:\"(?P<essid>.+)\"$"),
    re.compile(r"^Protocol:(?P<protocol>.+)$"),
    re.compile(r"^Mode:(?P<mode>.+)$"),
    re.compile(r"^Frequency:(?P<frequency>[\d.]+) (?P<frequency_units>.+) \(Channel (?P<channel>\d+)\)$"),
    re.compile(r"^Encryption key:(?P<encryption>.+)$"),
    re.compile(r"^Quality=(?P<signal_level>\d+)/(?P<signal_total>\d+)\s+Signal level=(?P<db>.+) d.+$"),
    re.compile(r"^Signal level=(?P<signal_level>\d+)/(?P<signal_total>\d+).*$"),
    
    re.compile(r"^IE: IEEE 802.11i/WPA2 Version (?P<wpa2>.+)$"),
    re.compile(r"^IE: WPA Version (?P<wpa>.+)$"),
    
    re.compile(r"Pairwise Ciphers \(.\) : (?P<cipher>.+)$"),
    re.compile(r"Authentication Suites \(1\) : (?P<auth>.+)$"),
]

# Runs the comnmand to scan the list of networks.
# Must run as super user.
# Does not specify a particular device, so will scan all network devices.
def scan(interface='wlan0'):
    cmd = ["iwlist", interface, "scan"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    points = proc.stdout.read().decode('utf-8')
    return points

# Parses the response from the command "iwlist scan"
def parse(content):
    cells = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        cellNumber = cellNumberRe.search(line)
        if cellNumber is not None:
            cells.append(cellNumber.groupdict())
            continue
        for expression in regexps:
            result = expression.search(line)
            if result is not None:
                cells[-1].update(result.groupdict())
                continue
    return cells