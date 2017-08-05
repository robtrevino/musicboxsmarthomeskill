import requests
import datetime
#### Settings ####
boxUrl = "http://internet_address_to_your_music_box:6680/mopidy/rpc"
postHeaders = { 'Content-Type' : 'application/json' }
timeOfSample = datetime.datetime.now().isoformat()[0:-4] + "Z"


def lambda_handler(event, context):
    print(str(event))
    #print(str(context))
    #access_token = event['directive']['payload']['scope']['token']
    global messageId
    messageId = event['directive']['header']['messageId']

    if event['directive']['header']['namespace'] == 'Alexa.Discovery':
        return handleDiscovery(context, event)

    elif event['directive']['header']['namespace'] == 'Alexa.Speaker':
        return handleSpeaker(context, event)

    elif event['directive']['header']['namespace'] == 'Alexa.PlaybackController':
        return handlePlaybackController(context, event)







##### The Handlers #########
def handleDiscovery(context, event):
    payload = ''
    header = {
        "namespace": "Alexa.Discovery",
        "name": "Discover.Response",
        "payloadVersion": "3",
        "messageId" : messageId
        }

    if event['directive']['header']['name'] == 'Discover':
        payload = {
            'endpoints':
            [
                {
                    "endpointId": "musicbox",
                    "manufacturerName": "Raspberry Pi",
                    "friendlyName": "Music Box",
                    "description": "Music Box running on the Raspberry pi",
                    "displayCategories": [  ],
                    "cookie": {
                        "key1": "arbitrary key/value pairs for skill to reference this endpoint.",
                        "key2": "There can be multiple entries",
                        "key3": "but they should only be used for reference purposes.",
                        "key4": "This is not a suitable place to maintain current endpoint state."
                    },
                    "capabilities":
                    [
                        {
                            "interface": "Alexa.Speaker",
                            "version": "1.0",
                            "type": "AlexaInterface"
                        },{
                            "interface": "Alexa.PlaybackController",
                            "version": "1.0",
                            "type": "AlexaInterface"
                        },
                    ]
                }
            ]
        }
    return { 'event': {'header': header, 'payload': payload }}

def handleSpeaker(context, event):

    ## Payload should always contain 'muted' and 'volume'
    muted = False

    if event['directive']['header']['name'] == 'SetVolume':
        newVolume = event['directive']['payload']['volume']
        setVolume(newVolume)


    elif event['directive']['header']['name'] == 'AdjustVolume':
        newVolume = event['directive']['payload']['volume'] + getVolume()
        setVolume(newVolume)

    elif event['directive']['header']['name'] == 'SetMute':
        muted = event['directive']['payload']['mute']
        newVolume = getVolume()
        setMute(muted)


    payload = speakerPayloadGenerator(newVolume = newVolume,muted = muted)

    return payload


def handlePlaybackController(context, event):

    ## Payload should always contain 'muted' and 'volume'


    if event['directive']['header']['name'] == 'FastForward':
        currTrack = getCurrentTrack()
        length = currTrack['length']
        currPos = getTimePos()
        newPos = currPos + 30000
        if (newPos > length):
            newPos = length
        seek(newPos)

    elif event['directive']['header']['name'] == 'Next':
        playNext()

    elif event['directive']['header']['name'] == 'Pause':
        pause()

    elif event['directive']['header']['name'] == 'Play':
        play()

    elif event['directive']['header']['name'] == 'Previous':
        playPrevious()

    elif event['directive']['header']['name'] == 'Rewind':
        currPos = getTimePos()
        newPos = currPos - 30000
        if (newPos < 0):
            newPos = 0
        seek(newPos)

    elif event['directive']['header']['name'] == 'StartOver':
        newPos = 0
        seek(newPos)

    elif event['directive']['header']['name'] == 'Stop':
        stop()

    payload = playbackControllerPayloadGenerator(messageId = event['directive']['header']['messageId'])
    return payload

##### The Mopidy calls #####

def speakerPayloadGenerator(newVolume,muted):
    payload = {
              "context": {
                "properties": [
                  {
                    "namespace": "Alexa.Speaker",
                    "name": "volume",
                    "value": newVolume,
                    "timeOfSample": timeOfSample,
                    "uncertaintyInMilliseconds": 0
                  },
                  {
                    "namespace": "Alexa.Speaker",
                    "name": "muted",
                    "value": muted,
                    "timeOfSample": timeOfSample,
                    "uncertaintyInMilliseconds": 0
                  }
                ]
              },
              "event": {
                "header": {
                  "messageId": messageId,
                  "namespace": "Alexa",
                  "name": "Response",
                  "payloadVersion": "3"
                },
                "payload": {
                }
              }
            }
    print(str(payload))
    return payload

def playbackControllerPayloadGenerator(messageId):
    payload = {
      "context": {
        "properties": []
      },
      "event": {
        "header": {
          "messageId": messageId,
          "namespace": "Alexa",
          "name": "Response",
          "payloadVersion": "3"
        },
        "payload": {
        }
      }
    }
    return payload

def getVolume():
    postBody = {
      "method": "core.mixer.get_volume",
      "jsonrpc": "2.0",
      "params": {},
      "id": 1
    }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    response = r.json()
    volume = response['result']
    return volume

def setVolume(newVolume):
    postBody = {
              "method": "core.mixer.set_volume",
              "jsonrpc": "2.0",
              "params": {
                "volume": int(newVolume)
              },
              "id": 1
            }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    return True

def setMute(muted):
    postBody = {
              "method": "core.mixer.set_mute",
              "jsonrpc": "2.0",
              "params": {
                "mute": muted
              },
              "id": 1
            }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    return True

def getCurrentTrack():
    postBody = {
      "method": "core.playback.get_current_track",
      "jsonrpc": "2.0",
      "params": {},
      "id": 1
    }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    response = r.json()
    track = response['result']
    return track

def getTimePos():
    postBody = {
      "method": "core.playback.get_time_position",
      "jsonrpc": "2.0",
      "params": {},
      "id": 1
    }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    response = r.json()
    timePos = response['result']
    return timePos

def seek(newPos):
    postBody = {
      "method": "core.playback.seek",
      "jsonrpc": "2.0",
      "params": {
        "time_position": newPos
      },
      "id": 1
    }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    response = r.json()
    return True

def playNext():
    postBody = {
      "method": "core.playback.next",
      "jsonrpc": "2.0",
      "params": {},
      "id": 1
    }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    response = r.json()
    return True

def pause():
    postBody = {
      "method": "core.playback.pause",
      "jsonrpc": "2.0",
      "params": {},
      "id": 1
    }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    response = r.json()
    return True

def play(tl_track = None, tlid = None):
    postBody = {
      "method": "core.playback.play",
      "jsonrpc": "2.0",
      "params": {
        "tl_track": tl_track,
        "tlid": tlid
      },
      "id": 1
    }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    response = r.json()
    return True

def playPrevious():
    postBody = {
      "method": "core.playback.previous",
      "jsonrpc": "2.0",
      "params": {},
      "id": 1
    }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    response = r.json()
    return True

def stop():
    postBody = {
      "method": "core.playback.stop",
      "jsonrpc": "2.0",
      "params": {},
      "id": 1
    }
    r = requests.post(url = boxUrl, headers = postHeaders, json = postBody)
    print(str(r.json()))
    response = r.json()
    return True
