#ifndef COMM_H
#define COMM_H

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include "esp_camera.h"

enum class Ports: uint16_t {
    READINGPORT = 8080,
    REGISTERPORT = 8081,
    SENSORSPORT = 8082,
    IMAGEPORT = 8083
};


enum class MIME: String {
    IMAGE_PNG = "image/png",
    IMAGE_JPG = "image/jpeg",
    APP_FORM = "application/x-www-form-urlencoded"
};


enum class HeaderFields: String {
    POST = "POST / HTTP/1.1",
    HOST = "Host: ",
    MIME = "Content-Type: ",
    CONNECTION = "Connection: close",
    LENGTH = "Content-Length: ",
    MAC = "MAC-address: ",
    TIMESTAMP = "Timestamp: "
};


struct Network {
    char* SSID;
    char* PASS;
    IPAddress HOST;
    IPAddress GATEWAY;
    IPAddress DNS;
};


/**
 * Connect to a HTTPS server.
 */
int connect(WiFiClientSecure *client, IPAddress HOST, IPAddress PORT);


/**
 * Connect to wifi Network and apply SSL certificate.
 */
int wifiSetup(WiFiClientSecure *client, char* SSID, char* PASS);


/**
 * Send readings from weather sensors to HOST on specified PORT. 
 */
int sendReadings(float* readings, int length, IPAddress HOST, IPAddress READINGPORT);


/**
 * Send statuses of weather sensors to HOST on specified PORT. 
 */
int sendStatuses(bool* statuses, int length, IPAddress HOST, IPAddress SENSORSPORT);


/**
 * Send Image buffer to HOST on specified PORT.
*/
int sendImage(camera_fb_t *fb, IPAddress HOST, IPAddress IMAGEPORT);


/**
 * Generate a header for a given HTTPS packet.
 */
String generateHeader(MIME type, int bodyLength, IPAddress HOST, String macAddress);


/**
 * Generate a header for a given HTTPS packet.
 * Some functions return size_t and therefore must be converted.
 * size_t can overflow int as its larger, but we only have 12MB of RAM, and the max image res
 * is like 720p.
 */
String generateHeader(MIME type, size_t bodyLength, IPAddress HOST, String macAddress);

/**
  * Get the current time and format the timestamp as MySQL DATETIME.
  * timeinfo is an empty struct whihc is filled by calling getLocalTime().
  */
String getTime()



/**
 * Server certificate for testing
 */
const char* TESTCERT  = "-----BEGIN CERTIFICATE-----\n"
"MIIDnDCCAoSgAwIBAgIEZS6f7TANBgkqhkiG9w0BAQsFADCBjzELMAkGA1UEBhMC\n" \
"U0UxFzAVBgNVBAgMDktyb25vYmVyZ3MgTGFuMRAwDgYDVQQHDAdWw6R4asO2MSQw\n" \
"IgYDVQQKDBtWw6R4asO2IExpbm5lYSBTY2llbmNlIFBhcmsxFzAVBgNVBAsMDklu\n" \
"bm92YXRpb24gTGFiMRYwFAYDVQQDDA1UYWRqIENhemF1Ym9uMB4XDTIzMTAxNzE0\n" \
"NTMzM1oXDTI0MTAxNjE0NTMzM1owgY8xCzAJBgNVBAYTAlNFMRcwFQYDVQQIDA5L\n" \
"cm9ub2JlcmdzIExhbjEQMA4GA1UEBwwHVsOkeGrDtjEkMCIGA1UECgwbVsOkeGrD\n" \
"tiBMaW5uZWEgU2NpZW5jZSBQYXJrMRcwFQYDVQQLDA5Jbm5vdmF0aW9uIExhYjEW\n" \
"MBQGA1UEAwwNVGFkaiBDYXphdWJvbjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCC\n" \
"AQoCggEBAJ75hDyV1aBn/kFie7t7VHSrCOr+VF8yWGxTau4sEU83FdO+0iCnLxyY\n" \
"71IQ+j6WNjIi/aAunwm7dTyXsnqvAghfFYmp4BbdU9/fnPA+4UM3Bmhw1ps20j/v\n" \
"5Vu60lSsF+v1MNKS/Odfop85LnKSrO0rx8mVz9Vw1lC0mH+l1aUVji7MHgbRhufU\n" \
"A/sc7KjEEz6KZqUVuVpLeUcKLA4UGgwW+3ruPmbGzml67SVgVEi0eQMvwC3o0FEk\n" \
"JNjsO8e+VV+JkKYlDthII677lqZzOwMVdG+bkj/RSgbFqa2nPJf7W2Kr0P1b+qmY\n" \
"mT7Y8BHRLGSnA/zfSA2EqVRmO/WbFmkCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEA\n" \
"Rb58Cwhpduz5yLK+4My2y4YYSuCEOl7UJu+9GnSi2M4z/NycO4JaQWmZvOQhR/iq\n" \
"jwp8u/2Z+Tz1Gamfy3+y03SvREjqykM8yZF2Oqss0qreEegcQWXmWEWTSm/B3MPu\n" \
"455lGyGwRxdiRAi7kHa+OavpVMbEnCHQ6Xnnx878JaTmpNRkovxGsPy7JAfezEsM\n" \
"86/5+Fp8+RLCKeLABiULAj0coSAFEeQBFr8fnvnpeRerinr1oSZ0KIcoR61bOTBD\n" \
"CNoBGribUny2YCkVhRxjBLfUxmZj0YEVrUfthVxFo5dGz6WRlG0KC2DY5MsiR/ZP\n" \
"we7BslkJ31ayjCwd2m6KQA==\n" \
"-----END CERTIFICATE-----\n";

const char* HOMECERT = "-----BEGIN CERTIFICATE-----\n" \
"MIIDtDCCApygAwIBAgIEZS0cNjANBgkqhkiG9w0BAQsFADCBmzELMAkGA1UEBhMC\n" \
"U0UxEDAOBgNVBAgMB1bDpHhqw7YxFzAVBgNVBAcMDktyb25vYmVyZ3MgTGFuMRcw\n" \
"FQYDVQQKDA5Jbm5vdmF0aW9uIExhYjEjMCEGA1UECwwaVsOkeGrDtiBMaW5uZSBT\n" \
"Y2llbmNlIFBhcmsxIzAhBgNVBAMMGlbDpHhqw7YgTGlubmUgU2NpZW5jZSBQYXJr\n" \
"MB4XDTIzMTAxNjExMTkxOFoXDTI0MTAxNTExMTkxOFowgZsxCzAJBgNVBAYTAlNF\n" \
"MRAwDgYDVQQIDAdWw6R4asO2MRcwFQYDVQQHDA5Lcm9ub2JlcmdzIExhbjEXMBUG\n" \
"A1UECgwOSW5ub3ZhdGlvbiBMYWIxIzAhBgNVBAsMGlbDpHhqw7YgTGlubmUgU2Np\n" \
"ZW5jZSBQYXJrMSMwIQYDVQQDDBpWw6R4asO2IExpbm5lIFNjaWVuY2UgUGFyazCC\n" \
"ASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAOmPRgG5VT38HxMl1cGOWthe\n" \
"yvX+/CBR1Eby9gw4pa/pmcBsmTCMHS4tSUJ7FBoxpo9SAEYibwqbUSUxW+AxD31L\n" \
"r1qRWLI/eVgum1XZq0DKmBy9B+4DV3o31RAcd0Z+/YmSg+1BnqldZMNoXR3kTRJG\n" \
"WZAH2utiOXeuTLwXmlbKfo/pPtjWMH2qw3zx52HjoagsLkJOsmPZmUXLXrSw/0lT\n" \
"FQ5rVkeAnXeqHJhwQQ5j+8jHyD3UfSIafEo/28MtUFfBIdC1vTARk+dvzLBlCnMd\n" \
"6M9fLn7ayDCJKypEI9c2exGI2/R8u+rY9NwOW721UWH2A4JsVFDfsSM3f3mVDnsC\n" \
"AwEAATANBgkqhkiG9w0BAQsFAAOCAQEAKu5Ygv/H7nCIwLOh3MANtjnM/1EjRqit\n" \
"r4f5SYpwOSXd4up/DdHEZkaPI9qFC59kvk3tLO/df9K8lIcgK3Cc4wP+5PRu4w+l\n" \
"4ANBJg2ZrEsTcczSNmpNv4Fuwh/deh4K31pdYKdZuebvcvuvDj0FLD68LnIyHUKR\n" \
"L/SZCQyiPGgJNJRxh2nOD+9NOVm7Mmy5T04o+Z7zMffEZ10GpzdeFQPXsjBR+SfF\n" \
"chqEjejTXO5fioYKZ3+r8dszFyaG9VIK7nG/Ptq8j85HGCdBBFsseh3eL/ctPJJv\n" \
"cH1vJGvHyQqRldaEKHy+ByIfZWirWkOq+6IFGmaPD557iEVFItMHHA==\n" \
"-----END CERTIFICATE-----\n";

#endif