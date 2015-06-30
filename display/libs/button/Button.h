#ifndef Button_h
#define Button_h

#include <Arduino.h>

class Button {
  public:
    Button();
    int read();
    void begin();
    void setPin(int pin);
    void setShort(int val);
    void setLong(int val);
    void setNotify(int pin);
  private:
    int _pin;
    int _ledPin;
    int _short;
    int _long;
    long _time;
    int _diff;
    int _blinked;
    void _blink();
};

#endif