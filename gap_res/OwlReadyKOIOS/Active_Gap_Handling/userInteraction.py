import requests

def APEWebserviceCall(phraseToDRS):
    print(phraseToDRS)
    # Make APE Webservice call with given ACE phrase
    urlToRequest = "http://attempto.ifi.uzh.ch/ws/ape/apews.perl?text=" + phraseToDRS + "&solo=drspp"
    # Get the DRS that is sent back
    r = requests.get(urlToRequest)
    returnedDRS = r.text.splitlines()
    DRSLines = []
    error = False
    # Iterate through all lines of returned DRS From the webservice
    for line in returnedDRS:
        line = line.strip()
        # Exclude first, useless line
        # Also skip empty lines (if line.strip() returns true if line is non-empty.)
        if line != '[]' and line.strip():
            # If "importance = "error"" is found,  then an error happened
            if line == "importance=\"error\"":
                error = True
            DRSLines.append(line)
    if error:
        return None
    else:
        return DRSLines


def ACEQuestiontoDRS(questionInput):
    questionLines = APEWebserviceCall(questionInput)
    return questionLines