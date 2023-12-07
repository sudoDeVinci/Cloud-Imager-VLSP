#include "comm.h"

Network network;
WiFiClientSecure client;

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
  writeFile(SD_MMC, "/servers/server.cfg","HOST=192.168.0.103\nCERT=/certs/server.cer");
  writeFile(SD_MMC, "/aps/server.cfg", "SSID=\"Asimov-2.4GHZ\"\nPASS=\"Asimov42\"\nDNS=8.8.8.8")
  writeFile(SD_MMC, "/profiles/server.cfg", "SERVER=\"server.cfg\"\nAP=\"server.cfg\"")
  
  const char* profile = "server.cfg";
  readProfile(SD_MMC, profile, network);

  Serial.println(network.SSID);
  Serial.println(network.PASS);
  Serial.println(network.DNS);
  Serial.println(network.HOST);
  readFile(SD_MMC, "/certs/server.cer");
}

void loop() {
  delay(1);
}
