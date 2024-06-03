from Devinci.METAR.structs import *
from typing import Dict
import json


def get_metar(airport: Airport = Airport.VAXJO, auth_key: str = None) -> Dict[str, Any] | None:
  if not auth_key:
    debug("No Api key specified.")
    return None
  
  headers = {
    'Authorization': f'{auth_key}'
  }

  url = f'https://avwx.rest/api/metar/{airport.value}?airport=true&format=json&remove=flight_rules%2Crunway_visibility%2Cother%2Cremarks%2Cremarks_info&onfail=nearest'
  reply = get(url, headers=headers)

  outjson = None
  try:
    outjson = json.loads(reply.content)
  except Exception as e:
     debug(f'{e} -> Couldn\'t encode json, check respons body.')
    
  return outjson
