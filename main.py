import websockets
import asyncio
import datetime
from pyngrok import ngrok
import juliandate as jd
import pytz


def dec_calculator(our_lat, moon_alt, moon_az):
    zenith_distance = 90 - moon_alt
    if moon_alt == 90.0:
        return our_lat
    elif 0 <= moon_az < 90.0:
        return our_lat + zenith_distance
    elif 90.0 < moon_az <= 180.0:
        return our_lat - zenith_distance


def ra_calculator(days, our_long, UT_hours):
    GMST = 100.4606184 + 0.9856473662862 * days + 15 * UT_hours
    return GMST + our_long  # Our Ra


async def handler(websocket):
    print("Client connected")
    try:
        while True:
            alt = float(input("Write the moon's altitude"))
            az = float(input("Write the moon's azimuth"))

            local_dt = datetime.datetime.now()
            utc = local_dt.astimezone(pytz.UTC)
            J2000 = jd.from_gregorian(2000, 1, 1, 12)
            today_julian = jd.from_gregorian(utc.year,
                                             utc.month,
                                             utc.day,
                                             utc.hour)
            total_days = today_julian - J2000

            coordinates = str(ra_calculator(total_days, long, today_julian)) + \
                          " " + str(dec_calculator(lat, alt, az))

            await websocket.send(coordinates)
            await asyncio.sleep(10)
    except websockets.exceptions.ConnectionClosed:
        print("Client just disconnected")


if __name__ == "__main__":
    lat = float(input('Write the latitude'))
    long = float(input("Write the longitude"))
    http_tunnel = ngrok.connect(8080, bind_tls=True)
    print("testing url is: ", http_tunnel.public_url)
    PORT = 8080
    start_server = websockets.serve(handler, "localhost", PORT)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
