#include <NewPing.h>

#define TRIGGER_PIN  7  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     8  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.


char payload[20];
// Hardcoding the data response for 1 sensor, i.e. depth sensor
// Two sensor data
byte sensor_response_payload[] = {0xA9, 0xBD, 0x01, 0x0B, \
                                 0x01, 0x02, 0x00, 0x00, 12, 34, 0x01, 0x00, 0x45, 0x67, 0xCB, \
                                  0xFD, 0xFF};
int payload_size = 17;
byte distance_int_idx = 8;
byte distance_frac_idx = 9;
// One sensor data
//byte sensor_response_payload[] = {0xA9, 0xBD, 0x01, 0x07, 0x01, 0x01, 0x00, 0x00, 12, 34, 0xCB, 0xFD, 0xFF};
//int payload_size = 13;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);  //ATmega -> host connection
  Serial1.begin(115200); //Atmega -> Linino connection

}


void loop() {
  byte cmd1, cmd2, msg_type;
  byte msg_len;
  byte tmp;

  while (Serial1.available() > 0) {
    cmd1 = Serial1.read();
    delay(1);  //Delay is necessary for serial port
    cmd2 = Serial1.read();
    delay(1);  //Delay is necessary for serial port
    
    if(cmd1 == 0xA9 && cmd2 == 0xBD) {
      Serial.print("Magic numbers are alright!\n");
      msg_type = Serial1.read();
      delay(1);
      if (msg_type == 0x00) {
        Serial.print("Msg type is REQUEST\n");
        msg_len = Serial1.read();
        delay(1);
        Serial.print("Msg len is: ");
        Serial.println(msg_len, DEC);
        Serial1.readBytes(payload, msg_len + 3);
        delay(1);
        //Serial.println(n, DEC);
        tmp = payload[0];
        if (tmp == 0x00) {
          Serial.print("Data request\n");
          // Gather sensor data here and send across to Linino Side
          gather_and_send_data();
          Serial.print("Data sent\n");
        }
          
        tmp = payload[1];  
        if (tmp == 0xCB) {
          Serial.print("Got EOD\n"); 
        }
        tmp = payload[2];
        Serial.print(tmp, HEX);
        tmp = payload[3];
        Serial.print(tmp, HEX);
      }
 
    } else {
        Serial.print("Received malformed packet!\n");
    }
  }    
}

void gather_and_send_data()
{
  byte diststr[2];
  Serial.println("Sending data to Linino: ");
  unsigned int pingtime = sonar.ping_median(10);
  float distance_in = pingtime / float(146); //sonar.convert_in(pingtime);
  printDouble(distance_in, 2, diststr);
  
  sensor_response_payload[distance_int_idx] = diststr[0];
  sensor_response_payload[distance_frac_idx] = diststr[1];
  Serial1.write(sensor_response_payload, payload_size);
}


void printDouble( double val, byte precision, byte *buff){
  // prints val with number of decimal places determine by precision
  // precision is a number from 0 to 6 indicating the desired decimial places
  // example: printDouble( 3.1415, 2); // prints 3.14 (two decimal places)

  Serial.print (int(val));  //prints the int part
  buff[0] = int(val) & 0xFF;
  
  if( precision > 0) {
    Serial.print("."); // print the decimal point
    unsigned long frac;
    unsigned long mult = 1;
    byte padding = precision -1;
    while(precision--)
       mult *=10;
       
    if(val >= 0)
      frac = (val - int(val)) * mult;
    else
      frac = (int(val)- val ) * mult;
    unsigned long frac1 = frac;
    while( frac1 /= 10 )
      padding--;
    byte tmp = padding;  //save it before it gets modified
    while(  padding--)
      Serial.print("0");
    Serial.print(frac,DEC) ;
    buff[1] = (frac & 0xFF);
    
    Serial.println("***");
    Serial.print(buff[0]);
    Serial.println(buff[1]);
    Serial.print("****");
  }
}

/* Original code for printDouble - saving for future reference 
void printDouble( double val, byte precision){
  // prints val with number of decimal places determine by precision
  // precision is a number from 0 to 6 indicating the desired decimial places
  // example: printDouble( 3.1415, 2); // prints 3.14 (two decimal places)

  Serial.print (int(val));  //prints the int part
  if( precision > 0) {
    Serial.print("."); // print the decimal point
    unsigned long frac;
    unsigned long mult = 1;
    byte padding = precision -1;
    while(precision--)
       mult *=10;
       
    if(val >= 0)
      frac = (val - int(val)) * mult;
    else
      frac = (int(val)- val ) * mult;
    unsigned long frac1 = frac;
    while( frac1 /= 10 )
      padding--;
    while(  padding--)
      Serial.print("0");
    Serial.print(frac,DEC) ;
  }
}
*/
