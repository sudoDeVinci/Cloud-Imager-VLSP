from Devinci.METAR.structs import Airport, Locale, get
import json


def get_QNH_hpa(
                airport: Airport = Airport.VAXJO,
                locale: Locale = Locale.English,
                version: str = "2.3",
                key: str = 'VOeVgaTHCcmuX4vuOS47tRLPEkOfPWTT'
                ) -> float|None:
    """
    This function retrieves the current QNH (Quasi-Neutral Atmospheric Pressure) in hPa for a given airport.
    It uses the METAR-TAF API to fetch the data.

    Parameters:
    - airport (Airport, optional): The airport for which to retrieve the QNH. Defaults to Airport.VAXJO.
    - locale (Locale, optional): The language locale for the API response. Defaults to Locale.English.
    - version (str, optional): The API version. Defaults to "2.3".
    - key (str, optional): The API key for authentication. Defaults to a predefined key.

    Returns:
    float|None: The current QNH in hPa, or None if an error occurred.

    Raises:
    Exception: If there is an error while fetching the data or parsing the JSON response.
    """

    outjson = None

    try:
        url = f"https://api.metar-taf.com/metar?api_key={key}&v={version}&locale={locale.value}&id={airport.value}&station_id={airport.value}"
        reply = get(url)
        outjson = json.loads(reply.content)['metar']['qnh']
    except Exception as e:
        print(f'{e} -> Couldn\'t encode json, check response body.')

    return outjson
