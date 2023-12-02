#include "comm.h"

Network network;
WiFiClientSecure client;

const char* cert = "-----BEGIN CERTIFICATE-----MIIDcjCCAlqgAwIBAgIEZWr6XzANBgkqhkiG9w0BAQsFADB7MQswCQYDVQQGEwJTRTEXMBUGA1UECAwOS3Jvbm9iZXJncyBMYW4xDjAMBgNVBAcMBVZheGpvMQ0wCwYDVQQKDARWTFNQMRwwGgYDVQQLDBNWTFNQIElubm92YXRpb24gTGFiMRYwFAYDVQQDDA1UYWRqIENhemF1Ym9uMB4XDTIzMTIwMjA5MzUyN1oXDTI0MTIwMTA5MzUyN1owezELMAkGA1UEBhMCU0UxFzAVBgNVBAgMDktyb25vYmVyZ3MgTGFuMQ4wDAYDVQQHDAVWYXhqbzENMAsGA1UECgwEVkxTUDEcMBoGA1UECwwTVkxTUCBJbm5vdmF0aW9uIExhYjEWMBQGA1UEAwwNVGFkaiBDYXphdWJvbjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAJ0CCq0aY35QjE1Vc5PYxA+L3DNkiHCQwF7R3K6thUM1HK0WZho2VPDmiFegDz/4dIXj4m3fDJjb60OLCafcxkogHHUWhwmbRN7h7aEJO17SGHjUGaoLg9H5O3iTiObPEDOoq6WrCV5sEcL0TUvbEQRxIczIVXiPEgviv5PcDzYJ3V9uFTIF96/XzxWUjkvnr+dTfcnvR8ZWEs1r/0amjJ6YBeBbg0uQ7rbN74dhyIxzfxXCwEQvQFXF6nc8FqGU9whNPoIaRUudMBH7SSLwY7jzUUHlbaonBUAPCphRV47eef3V5H4v9oyOOOmAWBf1UbOGlBv65at/4fqjM7ZP18kCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAmHUAPRWlh+CuI1nn7NSd4fR3EMkflWT5tuEO8QdZWpYnb8j2iP5Yz8cmSrVSI6o+MFinAYgkKLXgu+sC4WUE5ZHE562jlk6pFIJgPwA6f1d/eFroBaLDgx4nvEY947iwbmt6pOuBH+QUIId95SLb/v8HUp6SGTmRX1FNXSnDQhhxJCWCgqTdRjcEWpHgK3u1KsYN8pTzAV/fhS+hH+dXBC0/naFkpbqIetkF+iy7UcUDvVkyrR4fXn15kHgauRRwLvkDUh8WV1e3NT9SM11YJvZaqDpKAwr3Vl2fvXTJmOPsZqqzYDYWJbyZJFAhWuBJT9pwtefnvK+jP0aQ9l9wlQ==-----END CERTIFICATE-----";

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Setting up.");

  sdmmcInit();

  
  const char* profile = "home.cfg";
  readProfile(SD_MMC, profile, network);

  Serial.println(network.SSID);
  Serial.println(network.PASS);
  Serial.println(network.DNS);
  Serial.println(network.HOST);
}

void loop() {
  delay(1);
}
