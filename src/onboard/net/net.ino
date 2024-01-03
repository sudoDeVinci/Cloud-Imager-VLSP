#include "comm.h"

/**
 * My beautiful globals
 */
Network network;
WiFiClientSecure client;

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
    OTAUpdate(network, FIRMWARE_VERSION);
}

void loop {

    connect(network.CLIENT, network.HOST, 1312);

    if (!check(network.CLIENT, "Disconnected -> In connection phase")) {
        debugln(getResponse(clientnetwork.CLIENT));
    }

    if(network.CLIENT -> connected()) {
        debugln("Still connected -> Disconencted now");
        network.CLIENT -> stop();
    } else {
        debugln("Wasn't conencted to begin with");
        network.CLIENT -> stop();
    }
}