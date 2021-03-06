#include <OneWire.h>
#include <DallasTemperature.h>
#include <inttypes.h>

/********************************************************************/
// Data wire is plugged into pin 2 on the Arduino
#define ONE_WIRE_BUS 2
/********************************************************************/
// Setup a oneWire instance to communicate with any OneWire devices
// (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
/********************************************************************/
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);
/********************************************************************/
void setup(void)
{
  // start serial port
  Serial.begin(9600);
  sensors.begin();
}
void loop(void)
{
  sensors.requestTemperatures();
  for (uint8_t i = 0 ; i < sensors.getDeviceCount(); i++) {
    float temp = sensors.getTempCByIndex(i);
    if (temp > 0) {
      DeviceAddress deviceAddress;
      sensors.getAddress(deviceAddress, i);
      printAddress(deviceAddress);
      Serial.println("::" + String(temp, 2));
    }
  }
  delay(5000);
}


void printAddress(DeviceAddress deviceAddress)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    // zero pad the address if necessary
    if (deviceAddress[i] < 16) Serial.print("0");
    Serial.print(deviceAddress[i], HEX);
  }
}

