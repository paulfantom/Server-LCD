#include <Arduino.h>
#include <Button.h>

Button::Button() {
  _pin = 2;
  _short = 700;
  _long = 2500;
  _ledPin = -1;
  _blinked = 0;
}

void Button::begin() {
  pinMode(_pin,INPUT_PULLUP);
}

void Button::setPin(int pin) {
  _pin = pin;
}

void Button::setShort(int val) {
  _short = val;
}

void Button::setLong(int val) {
  _long = val;
}

void Button::setNotify(int pin) {
  _ledPin = pin;
  pinMode(_ledPin,OUTPUT);
  digitalWrite(_ledPin,HIGH);
}

int Button::read() {
  _time = millis();
  bool state = false;
  while (digitalRead(_pin) == LOW) {
    state = true;
    delay(10);
    if (_ledPin != -1) {
      if (millis() - _time > _short && _blinked == 0)
	_blink();
      if (millis() - _time > _long && _blinked == 1) {
	_blink();
	delay(300);
	_blink();
      }
    }
  }
  _blinked = 0;
  if (state) {
    _diff = millis() - _time;
    if (_diff < _short) {
      return 1;
    } else if (_diff > _short && _diff < _long) {
      return 2;
    } else {
      return 3;
    }
  } else {
    return 0;
  }
}

void Button::_blink() {
  digitalWrite(_ledPin,LOW);
  delay(300);
  digitalWrite(_ledPin,HIGH);
  _blinked++ ;
}