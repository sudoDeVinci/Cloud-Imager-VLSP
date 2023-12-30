#include "comm.h"

Network network;
WiFiClientSecure client;

const char* home_cert = R"(
-----BEGIN CERTIFICATE-----
MIIDtDCCApygAwIBAgIEZS0cNjANBgkqhkiG9w0BAQsFADCBmzELMAkGA1UEBhMC
U0UxEDAOBgNVBAgMB1bDpHhqw7YxFzAVBgNVBAcMDktyb25vYmVyZ3MgTGFuMRcw
FQYDVQQKDA5Jbm5vdmF0aW9uIExhYjEjMCEGA1UECwwaVsOkeGrDtiBMaW5uZSBT
Y2llbmNlIFBhcmsxIzAhBgNVBAMMGlbDpHhqw7YgTGlubmUgU2NpZW5jZSBQYXJr
MB4XDTIzMTAxNjExMTkxOFoXDTI0MTAxNTExMTkxOFowgZsxCzAJBgNVBAYTAlNF
MRAwDgYDVQQIDAdWw6R4asO2MRcwFQYDVQQHDA5Lcm9ub2JlcmdzIExhbjEXMBUG
A1UECgwOSW5ub3ZhdGlvbiBMYWIxIzAhBgNVBAsMGlbDpHhqw7YgTGlubmUgU2Np
ZW5jZSBQYXJrMSMwIQYDVQQDDBpWw6R4asO2IExpbm5lIFNjaWVuY2UgUGFyazCC
ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOmPRgG5VT38HxMl1cGOWthe
yvX+/CBR1Eby9gw4pa/pmcBsmTCMHS4tSUJ7FBoxpo9SAEYibwqbUSUxW+AxD31L
r1qRWLI/eVgum1XZq0DKmBy9B+4DV3o31RAcd0Z+/YmSg+1BnqldZMNoXR3kTRJG
WZAH2utiOXeuTLwXmlbKfo/pPtjWMH2qw3zx52HjoagsLkJOsmPZmUXLXrSw/0lT
FQ5rVkeAnXeqHJhwQQ5j+8jHyD3UfSIafEo/28MtUFfBIdC1vTARk+dvzLBlCnMd
6M9fLn7ayDCJKypEI9c2exGI2/R8u+rY9NwOW721UWH2A4JsVFDfsSM3f3mVDnsC
AwEAATANBgkqhkiG9w0BAQsFAAOCAQEAKu5Ygv/H7nCIwLOh3MANtjnM/1EjRqit
r4f5SYpwOSXd4up/DdHEZkaPI9qFC59kvk3tLO/df9K8lIcgK3Cc4wP+5PRu4w+l
4ANBJg2ZrEsTcczSNmpNv4Fuwh/deh4K31pdYKdZuebvcvuvDj0FLD68LnIyHUKR
L/SZCQyiPGgJNJRxh2nOD+9NOVm7Mmy5T04o+Z7zMffEZ10GpzdeFQPXsjBR+SfF
chqEjejTXO5fioYKZ3+r8dszFyaG9VIK7nG/Ptq8j85HGCdBBFsseh3eL/ctPJJv
cH1vJGvHyQqRldaEKHy+ByIfZWirWkOq+6IFGmaPD557iEVFItMHHA==
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
  createDir(SD_MMC, "/certs");
  createDir(SD_MMC, "/servers");
  createDir(SD_MMC, "/aps");
  createDir(SD_MMC, "/profiles");

  writeFile(SD_MMC, "/certs/server.cer", shitbox_cert);
  writeFile(SD_MMC, "/servers/server.cfg","HOST=192.168.8.110\nCERT=/certs/server.cer");
  writeFile(SD_MMC, "/aps/server.cfg", "SSID=\"VLSP-Innovation\"\nPASS=\"9a5mPA8bU64!\"\nDNS=8.8.8.8");
  writeFile(SD_MMC, "/profiles/server.cfg", "SERVER=\"server.cfg\"\nAP=\"server.cfg\"");


  writeFile(SD_MMC, "/certs/home.cer", home_cert);
  writeFile(SD_MMC, "/servers/home.cfg","HOST=192.168.0.101\nCERT=/certs/home.cer");
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
