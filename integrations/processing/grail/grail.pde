/*
 * Simple Client for recieving OSC messages from grail app
 * with syphon or spout server
 */

import oscP5.*;
import netP5.*;
import java.awt.event.KeyEvent;
import java.nio.charset.StandardCharsets;

OscP5 osc;
Server server;

PFont font;
PGraphics canvas;
Manager manager;
String message = "";

//===================================================================
//
//  Adjust configuration below for your needs
//
//===================================================================
int ADDRESS_PORT = 8001;
int FONT_SIZE = 72;
int COMPOSITION_WIDTH = 1280;
int COMPOSITION_HEIGHT = 720;


void settings(){
  size( COMPOSITION_WIDTH, COMPOSITION_HEIGHT, P3D );
}

void setup(){
  frameRate( 24 );

  osc = new OscP5( this, ADDRESS_PORT );
  font = createFont( "Arial Bold", FONT_SIZE, true );
  canvas = createGraphics( width, height, P3D );

  manager = new Manager();
  manager.setFont( font );

  server = new Server(this,
    "Grail Processing (" + width + "x" + height + ")",
    width, height);
}

/**
 * Draw a scene
 */
void draw(){
  manager.render( canvas );

  background( 0 );
  image( canvas, 0, 0, width, height );

  server.sendImage( canvas );
}

/**
 * Add message as State to State manager
 */
void pushState( String message ){

  manager.add( new State( message.toUpperCase() ) );

  if ( message.replaceAll("\\s+","").length() == 0 ){
    manager.setEffect( State.EFFECT_LAST );
  }

  redraw();
}

/**
 * Process input text and shortcuts
 */
void keyPressed() {
  if ( keyCode == KeyEvent.VK_TAB ){
    message = "";
    manager.add( new State( message ) );
    redraw();
  } else if ( keyCode == KeyEvent.VK_BACK_SPACE ){
    int l = message.length();

    if ( l > 1 ){
      message = message.substring(0, l - 1);
    } else {
      message = "";
    }
  } else if ( keyCode == KeyEvent.VK_SHIFT
   || keyCode == KeyEvent.VK_ALT
   || keyCode == KeyEvent.VK_CONTROL
   ) {
  } else {
    message = message + key;
  }

  pushState( message );
}

/**
 * Process incoming OSC messages
 */
void oscEvent( OscMessage message ){

  String addr = message.addrPattern();
    
  // parse new style bundle
  // for some reason it's not possible to get OscBundle
  if ( addr.indexOf("/clip/text/source") >= 0 || 
       addr.indexOf("/grail/message") >= 0 || 
       addr.indexOf("/cue/name") >= 0 ){
    String text = new String(message.get(0).blobValue(), StandardCharsets.UTF_8);

    pushState( text );
  }
}

void exit(){
  server.close();
  super.exit();
}
