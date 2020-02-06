/*
 * State drawing single text message
 * processing all animations and states
 */

class State {
  
  public final static int EFFECT_DEFAULT = 0;
  public final static int EFFECT_LAST = 1;

  public final static int TYPE_SONG = 0;
  public final static int TYPE_BIBLE = 1;
  
  public final static int STATE_IN = 0;
  public final static int STATE_STATIC = 1;
  public final static int STATE_OUT = 2;
  public final static int STATE_FINISHED = 3;
  
  int effect = 0;
  int type = 0;
  int state = -1;
  float time = 0.0;
  float start_time = 0.0;
  float opacity = 255;
  String text = "";
  float duration = 0.5;
  
  State ( String text ){
    this.text = text;
    this.setState( State.STATE_IN );
  }
  
  void setState( int state ){
    
    if ( this.state == State.STATE_IN && state == State.STATE_OUT ){
      this.start_time = millis() - (this.duration - this.time);
    } else if ( this.state < State.STATE_OUT && state != this.state ){
      this.start_time = millis();
    }
    
    this.state = state;
  }
  
  int getState(){
    return this.state;
  }
  
  boolean finished(){
    return this.state == State.STATE_FINISHED;
  }
  
  void setEffect( int effect ){
    this.effect = effect;
  }
 
  void update(){
    this.time = (millis() - this.start_time) / 1000;
    
    if ( this.state == State.STATE_OUT
     && this.effect == State.EFFECT_DEFAULT ){
      this.setState( State.STATE_FINISHED );
    }  
    
    if ( this.state == State.STATE_OUT 
     && this.effect == State.EFFECT_LAST
     && this.time > this.duration ){
      this.setState( State.STATE_FINISHED );
    } else {
    }
    
    if ( this.state == State.STATE_IN ){
      this.setState( State.STATE_STATIC );
    }  
  }
  
  void render( PGraphics canvas ){
     
    canvas.textAlign(CENTER, CENTER);
    canvas.textSize( 48 );
    
    float t = 1;
    float s = 1;
    
    if ( this.state == State.STATE_IN ){
      t = 1;
    }
    
    if ( this.state == State.STATE_OUT && this.effect == State.EFFECT_LAST ){
      t *= max(1 - this.time / this.duration, 0);
    }

    canvas.fill( 0, 0, 0, 255 * t );
    canvas.text( this.text, 
    width / 2 - (width * s)/2, 
    height / 2 - (height * s)/2 + 6, width * s, height * s);

    canvas.fill( 255, 255, 255, 255 * t );
    canvas.text( this.text, width / 2 - (width * s)/2, height / 2 - (height*s)/2, width * s, height * s);
  }

}