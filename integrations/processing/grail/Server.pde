/*
 * Server class interface
 *
 * Rename Server.pde-spout to Server.pde to use Spout implementation
 * or Server.pre-syphon to Server.pde to use Syphon on Mac
 */

class Server {
    
  Server ( PApplet applet, String name, int w, int h ){
  }
  
  void sendImage( PGraphics image ){
  }
  
  void close(){
  }
  
}
