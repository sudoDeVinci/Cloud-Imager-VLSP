#include "comm.h"

/**
 * My beautiful globals
 */
Network network;
WiFiClientSecure client;

void sleep_mins(float mins) {
  esp_sleep_enable_timer_wakeup(mins*60000000); //10 seconds
  esp_deep_sleep_start();
}

void setup() {
    Serial.begin(115200);
    debugln();
    debugln("Setting up.");

    sdmmcInit();

    /**
     * Read the profile config for the device network struct. 
     */
    const char* profile = "home.cfg";
    readProfile(SD_MMC, profile, network);// TODO: do something cause the profile reading failed.

    network.CLIENT = &client;

    wifiSetup(network.CLIENT, network.SSID, network.PASS, &sensors.status);
    const char* ntpServer = "pool.ntp.org";
    const char* timezone = "CET-1-CEST-2,M3.5.0/02:00:00,M10.5.0/03:00:00";
    configTime(0, 0, ntpServer);
    setenv("TZ", timezone, 1);

}

void loop {
    String timestamp = getTime(&network.TIMEINFO, &network.NOW, 10);

    sendTest(network.CLIENT, network.HOST, timestamp);
    if (!check(network.CLIENT, "Disconnected -> In connection phase")) {
        debugln(getResponse(clientnetwork.CLIENT));
    }

    if(network.CLIENT -> connected()) {
        debugln("Still connected -> Disconncted now");
        network.CLIENT -> stop();
    } else {
        debugln("Wasn't conencted to begin with");
        network.CLIENT -> stop();
    }

    debugln("Going to sleep!...");
    delay(50);
    sleep_mins(5);
}