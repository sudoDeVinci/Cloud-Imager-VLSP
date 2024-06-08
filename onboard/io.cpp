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

/**
 * Attempt to append to a given file.
 * Create the file if it doesn't exist.
 */
void writeToFile(fs::FS& fs, const String& path, const String& message) {
  File file;

  file = fs.open(path.c_str(), FILE_APPEND, true);
  if (!file) {
    file = fs.open(path.c_str(), FILE_WRITE, true);
    if (!file) {
      debugln("Couldn't open file for writing");
      return;
    }
  }

  if (file.println(message.c_str())) debugln("Message appended");
  else debugln("Message not appended");
  file.close();
}

/**
 * Split a String into an array of 5 Strings by a delimeter.
 */
 String* split(const String& s, const char* delimiter) {
  std::vector<String> values;

  int startIndex = 0;
  int endIndex = s.indexOf(delimiter);

  while (endIndex!= -1) {
    values.push_back(s.substring(startIndex, endIndex));
    startIndex = endIndex + 1;
    endIndex = s.indexOf(delimiter, startIndex);
  }

  values.push_back(s.substring(startIndex));

  // make fixed size string array from the vector
  // Determine the size of the vector
  size_t size = values.size();

  // Allocate memory for the array of String
  String* output = new String[size];

  // Copy the contents of the vector to the array
  for (size_t i = 0; i < size; ++i) {
    output[i] = values[i];
  }

  return output;
}

std::vector<String*> readFile(fs::FS &fs, const char * path){
  std::vector<String*> output;

  Serial.printf("\nReading file: %s\r\n", path);

  File file = fs.open(path);
  if(!file || file.isDirectory()){
    debugln("- failed to open file for reading");
    return output;
  }

  debugln("- read from file:");
  while(file.available()){
    String line = file.readStringUntil('\n');
    output.push_back(split(line, ","));
    debugln(line);
  }
  debugln();
  file.close();
  return output;
}


