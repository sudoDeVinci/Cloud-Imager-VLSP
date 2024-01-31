#include "io.h"

/**
 * Extract the double-quote enclosed string from a line in a conf file.
 */
const char* readString(const String& line) {
    // Find the position of '=' and the first double quote
    int equalsIndex = line.indexOf('=');
    int quoteStartIndex = line.indexOf('"', equalsIndex);

    // Check if '=' and '"' are found
    if (equalsIndex != -1 && quoteStartIndex != -1) {
        int quoteEndIndex = line.indexOf('"', quoteStartIndex + 1);

        // Check if the second double quote is found
        if (quoteEndIndex != -1) {
            int pathStartIndex = quoteStartIndex + 1;
            int pathLength = quoteEndIndex - pathStartIndex;

            // Extract the file path
            char* filePath = new char[pathLength + 1];  // +1 for null-terminator
            line.substring(pathStartIndex, quoteEndIndex).toCharArray(filePath, pathLength + 1);

            return filePath;
        }
    }

    return nullptr;
}

/**
 * Initialize the sdcard file system. 
 */
void sdmmcInit(void){
  SD_MMC.setPins(SD_MMC_CLK, SD_MMC_CMD, SD_MMC_D0);
  if (!SD_MMC.begin("/sdcard", true, true, SDMMC_FREQ_DEFAULT, 5)) {
    debugln("Card Mount Failed");
    return;
  }
  uint8_t cardType = SD_MMC.cardType();
  if(cardType == CARD_NONE){
      debugln("No SD_MMC card attached");
      return;
  }

  uint64_t cardSize = SD_MMC.cardSize() / (1024 * 1024);
  debugf("SD_MMC Card Size: %lluMB\n", cardSize);  
  debugf("Total space: %lluMB\r\n", SD_MMC.totalBytes() / (1024 * 1024));
  debugf("Used space: %lluMB\r\n", SD_MMC.usedBytes() / (1024 * 1024));
}