#include "comm.h"

Network network;
WiFiClientSecure client;

const char* cert = R"(
-----BEGIN CERTIFICATE-----
MIIDkjCCAnqgAwIBAgIEZWv4nTANBgkqhkiG9w0BAQsFADCBijELMAkGA1UEBhMC
U0UxFzAVBgNVBAgMDktyb25vYmVyZ3MgTGFuMQ4wDAYDVQQHDAVWYXhqbzEhMB8G
A1UECgwYVmF4am8gTGlubmUgU2NpZW5jZSBQYXJrMRcwFQYDVQQLDA5Jbm5vdmF0
aW9uIExhYjEWMBQGA1UEAwwNVGFkaiBDYXphdWJvbjAeFw0yMzEyMDMwMzQwMTNa
Fw0yNDEyMDIwMzQwMTNaMIGKMQswCQYDVQQGEwJTRTEXMBUGA1UECAwOS3Jvbm9i
ZXJncyBMYW4xDjAMBgNVBAcMBVZheGpvMSEwHwYDVQQKDBhWYXhqbyBMaW5uZSBT
Y2llbmNlIFBhcmsxFzAVBgNVBAsMDklubm92YXRpb24gTGFiMRYwFAYDVQQDDA1U
YWRqIENhemF1Ym9uMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzoQA
tHnLsUTdizNqWhVQveMwIo4EHsKrgYzwdBv3oL6F+xVKN5fJWJOkYJvaaze/+XQf
gBdMSy/0TL+1hEnsWHTDsc50oHx+jEPI6YgY4npRtsH0PZsLxDLVAKnY0djztlZf
YZFumTaSV/rDS6KFPBuOowbH60PMI7Ija620q/GGC3Nps4murojO/4ToAfZgKpWz
lFIkTaVF/NuiIGMsn7CHbPDBqH1tcyxIIa9kOO19EJtD1ywPHJuz40xz7pcUTBXf
wj6sm3PvLwdh0A16uKMyo2d3rT1UlnNMu9EDd9pQFFajSd6EQpngoQvigYEJVH2A
8Umf9VzuhsZl3jPXhwIDAQABMA0GCSqGSIb3DQEBCwUAA4IBAQBSDd49cwOX1lRi
3GCP8P5vRl9BIPdmzD3/tw1vNBdjFMDXPLLNMvFi7Ot/FPOR6nEDXsbJvRtXhMlg
qLgjJkT4kkP5qzMbnSNC2LvSXP1rhwrvjeuIuOefUKp3kHFm8DIeCjDfr8d47K9Y
guDjcBEjcL3XWtM8f206FVw+QKAbi4YE5qx/RoDqkGG5EgSzcDMHbOmhm3m/ZhkI
GWNWogZ/ienXI0AUh5b7lQBCoyKb1DK1eNVq+5ZhhREugynsdpO0n32pGsEo7Pvk
81kQzjZeUZ4g5SFCqtkPf9GzgkpbGhTBsiUUS+zTWve+G2AdQB60px2VeBhuKq/k
DKrOWu12
-----END CERTIFICATE-----)";

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Setting up.");

  sdmmcInit();

  writeFile(SD_MMC, "/certs/home.cer", cert);
  writeFile(SD_MMC, "/servers/home.cfg","HOST=192.168.0.105\nCERT=/certs/home.cer");
  const char* profile = "home.cfg";
  readProfile(SD_MMC, profile, network);

  Serial.println(network.SSID);
  Serial.println(network.PASS);
  Serial.println(network.DNS);
  Serial.println(network.HOST);
  readFile(SD_MMC, "/certs/home.cer");
}

void loop() {
  delay(1);
}
