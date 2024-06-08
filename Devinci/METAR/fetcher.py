from Devinci.METAR.structs import Airport, Locale, get

import json


def get_QNH_hpa(
                airport: Airport = Airport.VAXJO,
                locale: Locale = Locale.English,
                version: str = "2.3",
                key: str = 'VOeVgaTHCcmuX4vuOS47tRLPEkOfPWTT'
                ) -> float|None:

    url = f"https://api.metar-taf.com/metar?api_key={key}&v={version}&locale={locale.value}&id={airport.value}&station_id={airport.value}"

    reply = get(url)

    outjson = None

    try:
        outjson = json.loads(reply.content)['qnh']
    except Exception as e:
        print(f'{e} -> Couldn\'t encode json, check response body.')

    return outjson