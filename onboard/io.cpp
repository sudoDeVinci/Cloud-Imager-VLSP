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

void writeToLog(fs::FS& fs, const String& path, const String& message) {
  char* headers = "Timestamp,Temperature,Humidity,Pressure,Dewpoint";
  const char* filePath = path.c_str();
  
  if (!fs.exists(filePath)) {
    File file;
    debugf("Creating file: %s\n", filePath);
    file = fs.open(filePath, FILE_WRITE);
    if (!file) {
      debugln("Couldn't create file");
      return;
    }

    if (file.println(headers)) debugln("Headers written");
    else debugln("Headers not written");
    file.close();
  }

  writeToCSV(fs, path, message);
}

/**
 * Attempt to append to a given file.
 * Create the file if it doesn't exist.
 */
void writeToCSV(fs::FS& fs, const String& path, const String& message) {
  File file;

  file = fs.open(path.c_str(), FILE_APPEND, true);
  if (!file) {
    debugln("Couldn't open file for writing");
    return;
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

/**
 * Read the csv of past readings and return a vector of String arrays.
 */
std::vector<String*> readCSV(fs::FS &fs, const char * path) {
  std::vector<String*> output;

  debugf("\nReading file: %s\r\n", path);

  File file = fs.open(path);
  if(!file || file.isDirectory()){
    debugf("- failed to open %s for reading\r\n", path);
    return output;
  }

  // Skip the first line (headers).
  if (file.available()) file.readStringUntil('\n');

  while(file.available()){
    String line = file.readStringUntil('\n');
    output.push_back(split(line, ","));
  }
  debugln();
  file.close();
  return output;
}

String readFile(fs::FS &fs, const char * path) {
  debugf("\nReading file: %s\r\n", path);

  String output;

  File file = fs.open(path);
  if(!file || file.isDirectory()){
    debugf("- failed to open %s for reading\r\n", path);
    return output;
  }

  while(file.available()){
    char ch = file.read();
    output.concat(ch);
  }

  debugln();
  file.close();
  return output;
}

/**
 * Write an image buffer into a jpg file. 
 */

void writejpg(fs::FS &fs, const char * path, const uint8_t* buf, size_t size) {
  File file = fs.open(path, FILE_WRITE);
  if(!file){
    debugf("- failed to open %s for writing\r\n", path);
    return;
  }
  file.write(buf, size);
  debugf("Saved file to path: %s\r\n", path);
}

/**
 * Read an image buffer from a jpg file. 
 */
uint8_t* readjpg(fs::FS &fs, const char* path) {
  uint8_t* output;

  debugf("\nReading file: %s\r\n", path);

  File file = fs.open(path);
  if(!file || file.isDirectory()){
    debugf("- failed to open %s for reading\r\n", path);
    return output;
  }

  const size_t fileSize = file.size();

  while(file.available()){
    file.read(output, fileSize);
  }
  debugln();
  file.close();
  return output;
}