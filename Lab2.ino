#include <Wire.h>

struct Buzzer {
    int Pin = 2;
    int length = 100;
    bool playing = false;
} Buzzer;

struct Joystick {
  int PinX = A0;
  int PinY = A1;
  char Direction = 'C';
  char PrevDirection = 'C';
} Joystick;

struct MPU {
  int Address = 0x68;
  int ACCEL_XOUT_H = 0x3B;
  int ACCEL_CONFIG = 0x1C;
  int GYRO_XOUT_H = 0x43;
  int GYRO_CONFIG = 0x1B;
  int PWR_MGMT_1 = 0x6B;
  char Direction = 'C'; 
  char PrevDirection = 'C';
} MPU;

void mpuWrite(int reg, int data) {
  Wire.beginTransmission(MPU.Address);
  Wire.write(reg);
  Wire.write(data);
  Wire.endTransmission();
}

int readWord(int reg) {
  Wire.beginTransmission(MPU.Address);
  Wire.write(reg);
  Wire.endTransmission(false);

  Wire.requestFrom(MPU.Address, 2);  // Request 2 bytes
  int value = (Wire.read() << 8) | Wire.read();  // Combine MSB and LSB
  return value;
}


void setup() {
  pinMode(Joystick.PinX, INPUT);
  pinMode(Joystick.PinY, INPUT);
  /*Buzzer*/
  pinMode(Buzzer.Pin, OUTPUT);
  /*Wake Up MPU*/
  mpuWrite(MPU.PWR_MGMT_1, 0x00);  
  mpuWrite(MPU.ACCEL_CONFIG, 0x00); 
  mpuWrite(MPU.GYRO_CONFIG, 0x00);   
  delay(100);
 
  cli();//stop interrupts
  //SETUP TIMER 1
  TCCR1A = 0;// set entire TCCR1A register to 0
  TCCR1B = 0;
  TCNT1  = 0;
  OCR1A = 249;
  TCCR1B |= (1 << WGM12);
  TCCR1B |= (1 << CS11) | (1 << CS10);  
  TIMSK1 |= (1 << OCIE1A);
  /*Start Serial*/
  Serial.begin(9600);
  /*allow interrupts*/
  sei();
}

int time = 0;
ISR(TIMER1_COMPA_vect) {
  if((Buzzer.playing) && (time < Buzzer.length)) {
      if(time == 0) {
        digitalWrite(Buzzer.Pin, HIGH);
      }
      time++;
  }
  else if((Buzzer.playing) && (time >= Buzzer.length)) {
      digitalWrite(Buzzer.Pin, LOW);
      Buzzer.playing = false;
      time = 0;
  }
}

void get_joystick_direction() {
    long x = analogRead(Joystick.PinX);
    long y = analogRead(Joystick.PinY);
    bool x_centered = false;
    bool y_centered = false;

    if(x < 100) {
        Joystick.Direction = 'L';
    }
    else if(x > 800) {
        Joystick.Direction = 'R';
    }
    else {
      x_centered = true;
    }

    if(y < 100) {
        Joystick.Direction = 'U';
    }
    else if(y > 800) {
        Joystick.Direction = 'D';
    }
    else {
      y_centered = true;
    }

    if(x_centered && y_centered) {
        Joystick.Direction = 'C';
        Joystick.PrevDirection = 'C';
    }

    switch(Joystick.Direction) {
          case 'L':
                if(Joystick.PrevDirection != 'L') {
                    Serial.println("JOYSTICK_LEFT");
                    Joystick.PrevDirection = 'L';
                }
          break;
          case 'R':
                if(Joystick.PrevDirection != 'R') {
                    Serial.println("JOYSTICK_RIGHT");
                    Joystick.PrevDirection = 'R';
                }
          break;
           case 'U':
                if(Joystick.PrevDirection != 'U') {
                    Serial.println("JOYSTICK_UP");
                    Joystick.PrevDirection = 'U';
                }
          break;
          case 'D':
                if(Joystick.PrevDirection != 'D') {
                  Serial.println("JOYSTICK_DOWN");
                  Joystick.PrevDirection = 'D';
                }
          break;
   }

}

void set_mpu_direction(char direction, char* str) {
   if(MPU.PrevDirection != direction) {
      Serial.println(str);
      MPU.PrevDirection = direction;
  }
}

void get_mpu_direction() {
    int AccelX = readWord(MPU.ACCEL_XOUT_H);
    int AccelY = readWord(MPU.ACCEL_XOUT_H + 2);
    int AccelZ = readWord(MPU.ACCEL_XOUT_H + 4);
    int acc_threshold = 20000; /*shake sensitivity*/

    int GYRO_XOUT_H = MPU.GYRO_XOUT_H;
    int GyroX = readWord(GYRO_XOUT_H);
    int GyroY = readWord(GYRO_XOUT_H + 2);
    int GyroZ = readWord(GYRO_XOUT_H + 4);
    int gy_threshold = 8000;
    
    char direction;
    if(GyroY < (-1 * gy_threshold)) {
        direction = 'L';
    }
    else if(GyroY  > gy_threshold) {
        direction = 'R';
    }

    if(GyroX < (-1 * gy_threshold)) {
        direction = 'D';
    }
    else if(GyroX  > gy_threshold) {
        direction = 'U';
    }

   long magnitude = sqrt((long)AccelX * AccelX + (long)AccelY * AccelY + (long)AccelZ * AccelZ);
   if(magnitude > acc_threshold) {
        direction = 'S';
   }
   //Serial.println(magnitude);
   switch(direction) {
           case 'L':
                set_mpu_direction('L', "MPU_LEFT");
          break;
          case 'R':
                set_mpu_direction('R', "MPU_RIGHT");
          break;
          case 'U':
                set_mpu_direction('U', "MPU_UP");
          break;
          case 'D':
               set_mpu_direction('D', "MPU_DOWN");
          break;
          case 'S':
               set_mpu_direction('S', "MPU_SHAKE");
          break;
   }
   if(direction == 'S') {
      delay(1000);
   } else {
      delay(100);
   }
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readString();  // Read the incoming string
    if(input.equals("BUZZ\n") && (!Buzzer.playing)) {
        Buzzer.playing = true;
    }
  }
  get_mpu_direction();
  get_joystick_direction(); 
}
