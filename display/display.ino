#include <LiquidCrystal.h>
#include <Button.h>
#include <Time.h>
#include <Arduino.h>
#include <avr/wdt.h>
#include <Timer.h>

const int ILLUMINATION = 2;
const int BUTTON = 12; // 3;
const int LED_PIN = 4;

const int RS = A0; // A5;
const int EN = A1; // A4;
const int D4 = A2; // A3;
const int D5 = A3; // A2;
const int D6 = A4; // A1;
const int D7 = A5; // A0;
const int SIZE = 34;

Timer t;
const int PING_TIMEOUT = 300; //seconds
int PING = 0;

LiquidCrystal lcd(RS, EN, D4, D5, D6, D7);

boolean led_reason[2] = {false, false};

int screenCurr = 0;
boolean cycle = true;
int loopCounter = 0;
int screenChangeTime = 60; // *50ms
const int screenCount = 8;
char screens[8][SIZE] = {
    " MCU RESTARTED  \n power failure? ", "       ..       \n       ^^       ",
    "      ....      \n      ^^^^      ", "     ......     \n     ^^^^^^     ",
    "    ........    \n    ^^^^^^^^    ", "   ..........   \n   ^^^^^^^^^^   ",
    "  ............  \n  ^^^^^^^^^^^^  ", " .............. \n ^^^^^^^^^^^^^^ "};

boolean update = false;
int last = 1;

// Notifications
boolean LOCK = true;
//boolean LED = true;
boolean BACKLIGHT = false;
boolean ERROR = true;

// set up button
Button button;

void setup() {
  //clear watchdog timer
  wdt_disable();
  delay(2 * 1000); //debug WDT
  
  setTime(14, 13, 12, 30, 10, 2015);
  lcd.begin(16, 2);
  Serial.begin(9600);
  clearInBuffer();

  char buf[17];
  strcpy(screens[0], getFullDate(buf));
  screens[0][16] = '\n';

  button.setPin(BUTTON);
  button.setNotify(ILLUMINATION);
  button.begin();

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  // pinMode(8,OUTPUT);
  // digitalWrite(8,HIGH);

  ledON(0);
  
  pinMode(10, OUTPUT);
  digitalWrite(10, HIGH);

  t.every(1000, checkHost);

  wdt_enable(WDTO_8S);
}

void loop() {
  wdt_reset();
  
  // prevent blinking characters on screen
  // or render on new message
  if (last != screenCurr || update) {
    // if (true){
    render(screens[screenCurr]);
    last = screenCurr;
    update = false;
  }

  // wait for ACK, lock other activity
  if (LOCK) {
    //if (STP == true)
    //  Serial.println("STP");
    if (button.read() == 0)
      return;
    else
      delay(10);
    LOCK = false;
    ERROR = false;
    if (BACKLIGHT == true) {
      delay(500);
      BACKLIGHT = false;
    }
    ledOFF(-1);
    //Serial.println("CON");
    //STP = false;
  }

  delay(100);
  // get operation mode
  // nothing            -> ?????
  // short button click -> change screen
  // longer click       -> cycle screens
  // longest press      -> clear LCD
  switch (button.read()) {
  case 0:
    if (loopCounter == screenChangeTime - 1) {
      ++screenCurr %= screenCount;
    }
    break;
  case 1: {
    ++screenCurr %= screenCount;
    cycle = false;
    break;
  }
  case 2: {
    cycle = cycle ? false : true;
    ++screenCurr %= screenCount;
    break;
  }
  case 3: {
    lcd.clear();
    break;
  }
  };

  // find if it is time to change screen in cycle mode
  if (cycle)
    loopCounter = (loopCounter + 1) % screenChangeTime;
  else
    loopCounter = 0;

  t.update();
}

void checkHost() {
  if (PING >= PING_TIMEOUT)
    error("HOST PING FAILED");
  else 
    PING++;
}

void ledON(int reason) {
  led_reason[reason] = true;
  digitalWrite(LED_PIN, HIGH);
}

void ledOFF(int reason) {
  if (reason == -1){
    for (int i = 0; i < sizeof(led_reason); i++)
      led_reason[i] == false;
  } else {
    led_reason[reason] = false;
    for (int i = 0; i < sizeof(led_reason); i++) {
      if (led_reason[i] == true)
        return;
    }
  }
  digitalWrite(LED_PIN, LOW);
}

// show message on screen
void render(char *msg) {
  delay(100); // ???
  lcd.clear();
  int i = 0;
  while (msg[i] != '\0' && i < SIZE) {
    if (msg[i] == '\n' || i == 16) {
      lcd.setCursor(0, 1);
      if (i == 16 && msg[i] != '\n')
        lcd.write(msg[i]);
    } else
      lcd.write(msg[i]);
    i++;
  }
}

char* intToCharArray(char *buf, int in, char padding) {
  //works only if int < 100
  char out[] = "  ";
  if (in > 9) {
    int s = in / 10;
    out[0] = (char)(s + 48);
    out[1] = (char)(in - s * 10 + 48);    
  } else if (in < 10) {
    out[0] = padding;
    out[1] = (char)(in + 48);
  }
  strcpy(buf,out);
  return buf;
}

char *getHour(char *buf) {
  //char curr[6];
  char buf2[3];
  strcpy(buf, intToCharArray(buf2, hour(), '0'));
  buf[2] = ':';
  buf[3] = '\0';
  strcat(buf, intToCharArray(buf2, minute(), '0'));
  return buf;
}

char *getFullDate(char *buf) {
  int start = 0;
  char date[17] = "--- dd.MM  hh:mm";
  strcpy(date,dayShortStr(weekday()));
  date[3] = ' ';
  date[4] = '\0';
  char buf2[3];
  strcpy(date + 4, intToCharArray(buf2, day(), '0'));
  date[6] = '.';
  date[7] = '\0';
  strcpy(date + 7, intToCharArray(buf2, month(), '0'));
  date[9] = ' ';
  date[10] = ' ';
  date[11] = '\0';
  char buf3[6];
  strcpy(date + 11, getHour(buf3));
  //Serial.println(date);
  strcpy(buf,date);
  return buf;
}

void parse(char s, int pos) {
  char c;
  char buff[SIZE];
  delay(70);  // wait for Serial buffer to fill (67ms)
  for (int i = 0; i < SIZE - 1; i++) {
    if (Serial.available()){
      c = Serial.read();
      /*if (c == '\0'){
        Serial.println("FIN null too soon"); //end of msg too soon
        return;
      }*/
    } else {
      Serial.println("FIN msg too short"); //msg too short
      return;
    }
    buff[i] = c;
  }
  buff[SIZE-1] = '\0';

  if (Serial.available()) {
    c = Serial.read(); //get checksum
  } else {
    Serial.println("FIN no checksum"); //no checksum
    return;
  }
  /*if (Serial.available()){
    if(Serial.read() != '\0'){
      Serial.println("FIN no terminator"); //no terminator detected
      return;
    }
  }*/
  buff[33] = s;
  //Serial.println(checksum(buff, SIZE));
  if (c == checksum(buff, SIZE)) {
    buff[33] = '\0';
    strncpy(screens[pos],buff,34);
    Serial.println("ACK");
  } else
    Serial.println("RST wrong checksum");
  return;
}

char checksum(char* st, int len) {
  byte sum = 0;
  for (int i = 0; i< len; i++) {
    sum += st[i];
  }
  //sum %= 256; //no need, 8-bit var takes care of it
  return (char)sum;
}

void syncTime() {
  delay(70);
  // if time sync available from serial port, update time
  while (Serial.available() >= 11) {
    //char c = Serial.read();
    char c;
    char chksm = 0;
    char buf[12] = "T0000000000";
    time_t pctime = 0;
    for (int i = 1; i < 11; i++) {
      buf[i] = Serial.read();
      c = buf[i];
      if (c >= '0' && c <= '9') {
        pctime = (10 * pctime) + (c - '0'); // convert digits to a number
      }
    }
    chksm = Serial.read();

    //validate checksum
    if (chksm == checksum(buf,11)){
      setTime(pctime); /* Sync Arduino clock to the time 
                        received on the serial port*/
      Serial.println("ACK");
    } else
      Serial.println("RST time msg invalid checksum");
  }
}

void error(char* msg) {
  screenCurr = 7; // ERROR SCREEN
  LOCK = true;
  ERROR = true;
  ledON(0);
  char buf[17];
  strcpy(screens[screenCurr], getFullDate(buf));
  screens[screenCurr][16] = '\n';;
  strcpy(screens[screenCurr] + 17, msg);
}

void clearInBuffer() {
  delay(70); //be sure buffer is filled (should be 67ms)
  while (Serial.available())
    Serial.read();
}

void serialEvent() {
  PING = 0;
  int pos = 0;
  if (Serial.available()) {
    char c = Serial.read();
    switch (c) {
    case '~':
      pos = 7;
      screenCurr = pos;
      LOCK = true;
      ledON(0);
      break;
    case '!':
      pos = 0;
      screenCurr = pos;
      ledON(0);
      break;
    case '@':
      pos = 0;
      ledOFF(0);
      break;
    case '#':
      pos = 1;
      break;
    case '$':
      pos = 2;
      break;
    case ')':
      pos = 2;
      screenCurr = pos;
      cycle = false;
      break;
    case '%':
      pos = 3;
      break;
    case '(':
      pos = 3;
      screenCurr = pos;
      cycle = false;
      break;
    case '^':
      pos = 4;
      ledOFF(1);
      break;
    case '/':
      pos = 4;
      ledON(1);
      screenCurr = pos;
      cycle = false;
      break;
    case '&':
      pos = 5;
      break;
    case '*':
      pos = 6;
      break;
    case '?':
      if (ERROR == true){
        clearInBuffer();
        Serial.println("FIN");
        return;
      }
      pos = 7;
      break;
    case 'T':
      syncTime();
      clearInBuffer();
      return;
    case 'H':
      error(" daemon HALTED! ");
      Serial.println("ACK");
      clearInBuffer();
      return;
    case 'P':
      // pong
      Serial.println("PONG");
      clearInBuffer();
      return;
    default:
      Serial.println("FIN wrong start");
      clearInBuffer();
      return;
    };
    parse(c,pos);
    clearInBuffer();
    update = true;
    delay(10);
  }
}
