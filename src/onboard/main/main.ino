#include "comm.h"

Network network;
WiFiClientSecure client;

const char* home_cert = R"(
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

const char* shitbox_cert = R"(
------BEGIN CERTIFICATE-----
MIIDnjCCAoagAwIBAgIEZXEiATANBgkqhkiG9w0BAQsFADCBkDELMAkGA1UEBhMC
U0UxFzAVBgNVBAgMDktyb25vYmVyZ3MgTGFuMRAwDgYDVQQHDAdWw6R4asO2MSQw
IgYDVQQKDBtWw6R4asO2IExpbm5lYSBTY2llbmNlIFBhcmsxGDAWBgNVBAsMD0lu
bm92YXRpb25hIExhYjEWMBQGA1UEAwwNVGFkaiBDYXphdWJvbjAeFw0yMzEyMDcw
MTM4MDhaFw0yNDEyMDYwMTM4MDhaMIGQMQswCQYDVQQGEwJTRTEXMBUGA1UECAwO
S3Jvbm9iZXJncyBMYW4xEDAOBgNVBAcMB1bDpHhqw7YxJDAiBgNVBAoMG1bDpHhq
w7YgTGlubmVhIFNjaWVuY2UgUGFyazEYMBYGA1UECwwPSW5ub3ZhdGlvbmEgTGFi
MRYwFAYDVQQDDA1UYWRqIENhemF1Ym9uMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A
MIIBCgKCAQEAyEgLno1iUp22CfmvissqKuygPq2hUqJ3n+8syuUsWyLuoX5Gvuaa
U4giKUOP4ieXdtDH9JohSVgqwTzZcGahwZEUngFrV6s/w/YfJy2x0DvduyQJDjBz
2Q1BrmJav2xZRswZ66VDrBovwKjVPKMCWeVJpR6l289ekvsjvh95pOFPqXZ+jD0g
nOotbZmJCgS98ztyqtvYHOE3kEvhzCU/uggQ4ZJc6pV8p++hgPGMyU8RkNASIEYa
tBzq8bVH0/CwY5m/l5Ewz6MEoQORRGFhd6j0Y556yftjbXL5bFkmMfsy6QUkd6gF
t4uTrPrEaNSfOZu4qRUgH/TFnYd2HJ8eNwIDAQABMA0GCSqGSIb3DQEBCwUAA4IB
AQAJGyvZFebrwRTmtGh9neINPKlSOMW2DLNcqLMyuBt8bTAdBq/Hf/z524jeSiTu
PByjzbZcJCH1kNhebs0a86uHv/dRBA5Yr/MuqOk4mL/ENfavPTr1GbWjZC7L+K3P
NMi+FQomPH1MaISYahNyII69CV1vZ2MvK0ZyFB+XM0TZDGEyIH5IrDhfLz9cpSKF
OFTpol6kaIkpQg49nyAGzPGEMA9STa2ydBeejFMdZCRRDLgY9h5xYBH4/o2MM+Fh
hUXWRtMt2/x9sGa9WnapoWFjtDhGO76I0u10ATI0jrY/arMMSUWtlhEbJrSsQ8F2
+4FYojHKO+QpBhNxESQROnD9
-----END CERTIFICATE-----)";

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("Setting up.");

  sdmmcInit();

  writeFile(SD_MMC, "/certs/server.cer", shitbox_cert);
  writeFile(SD_MMC, "/servers/server.cfg","HOST=192.168.8.110\nCERT=/certs/server.cer");
  writeFile(SD_MMC, "/aps/server.cfg", "SSID=\"VLSP-Innovation\"\nPASS=\"9a5mPA8bU64!\"\nDNS=8.8.8.8");
  writeFile(SD_MMC, "/profiles/server.cfg", "SERVER=\"server.cfg\"\nAP=\"server.cfg\"");


  writeFile(SD_MMC, "/certs/home.cer", home_cert);
  writeFile(SD_MMC, "/servers/home.cfg","HOST=192.168.0.105\nCERT=/certs/home.cer");
  writeFile(SD_MMC, "/aps/home.cfg", "SSID=\"Asimov-2.4GHZ\"\nPASS=\"Asimov42\"\nDNS=8.8.8.8");
  writeFile(SD_MMC, "/profiles/home.cfg", "SERVER=\"home.cfg\"\nAP=\"home.cfg\"");
  
  Serial.println('\n');
  const char* profile = "server.cfg";
  readProfile(SD_MMC, profile, network);
  Serial.println("Loading Server Cert: ");
  Serial.println(network.SSID);
  Serial.println(network.PASS);
  Serial.println(network.DNS);
  Serial.println(network.HOST);
  readFile(SD_MMC, "/certs/server.cer");
  Serial.println('\n');
  profile = "home.cfg";
  readProfile(SD_MMC, profile, network);
  Serial.println("Loading Server Cert: ");
  Serial.println(network.SSID);
  Serial.println(network.PASS);
  Serial.println(network.DNS);
  Serial.println(network.HOST);
  readFile(SD_MMC, "/certs/home.cer");
}

void loop() {
  delay(1);
}
