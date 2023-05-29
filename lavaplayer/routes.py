
GET_PLAYERS = "/v3/sessions/{sessionId}/players"  # GET
GET_PLAYER = "/sessions/{sessionId}/players/{guildId}"  # GET
UPDATE_PLAYER = "/v3/sessions/{sessionId}/players/{guildId}?noReplace=true"  # PATCH
"""Whether to replace the current track with the new track. Defaults to `false`"""
DESTROY_PLAYER = "/v3/sessions/{sessionId}/players/{guildId}"  # DELETE
UPDATE_SESSION = "/v3/sessions/{sessionId}"  # PATCH
TRACK_LOADING = "/v3/loadtracks?identifier={identifier}"  # GET
TRACK_DECODEING = "/v3/decodetrack?encodedTrack={encodedTrack}"  # GET
TRACKS_DECODEING = "/v3/decodetracks"  # POST
INFO = "/v3/info"  # GET
STATS = "/v3/stats"  # GET
VERSION = "/version"  # GET
ROUTEPLANNER = "/v3/routeplanner/status"  # GET
UNMARK_FAILED_ADDRESS = "/v3/routeplanner/free/address"  # POST
UNMARK_ALL_FAILED_ADDRESS = "/v3/routeplanner/free/all"  # POST

