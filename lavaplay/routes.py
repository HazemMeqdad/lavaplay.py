
GET_PLAYERS = "/sessions/{sessionId}/players"  # GET
GET_PLAYER = "/sessions/{sessionId}/players/{guildId}"  # GET
UPDATE_PLAYER = "/sessions/{sessionId}/players/{guildId}?noReplace={noReplace}"  # PATCH
"""Whether to replace the current track with the new track. Defaults to `false`"""
DESTROY_PLAYER = "/sessions/{sessionId}/players/{guildId}"  # DELETE
UPDATE_SESSION = "/sessions/{sessionId}"  # PATCH
TRACK_LOADING = "/loadtracks?identifier={identifier}"  # GET
TRACK_DECODEING = "/decodetrack?encodedTrack={encodedTrack}"  # GET
TRACKS_DECODEING = "/decodetracks"  # POST
INFO = "/info"  # GET
STATS = "/stats"  # GET
VERSION = "/version"  # GET
ROUTEPLANNER = "/routeplanner/status"  # GET
UNMARK_FAILED_ADDRESS = "/routeplanner/free/address"  # POST
UNMARK_ALL_FAILED_ADDRESS = "/routeplanner/free/all"  # POST

