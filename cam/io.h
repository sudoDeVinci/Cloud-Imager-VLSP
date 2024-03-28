#pragma once
#ifndef IO_H
#define IO_H

#include <Arduino.h>

#define DEBUG 1

#if DEBUG == 1
#define debug(...) Serial.print(__VA_ARGS__)
#define debugln(...) Serial.println(__VA_ARGS__)
#define debugf(...) Serial.printf(__VA_ARGS__)
#else
#define debug(...)
#define debugln(...)
#define debugf(...)
#endif


#define SD_MMC_CMD  38 //Please do not modify it.
#define SD_MMC_CLK  39 //Please do not modify it. 
#define SD_MMC_D0   40 //Please do not modify it.
#define CERT_FOLDER "//certs"
#define SERVER_FOLDER "//servers"
#define AP_FOLDER "//aps"
#define PROFILE_FOLDER "//profiles"

#endif