/*
 *
 *
 */

class Manager {
  
  ArrayList<State> states = new ArrayList<State>();
  PFont font;
  
  Manager (){
  }
  
  void add( State state ){
    
    for ( int i = this.states.size() - 1; i >= 0; i-- ){
      State item = this.states.get( i );
      
      item.setState( State.STATE_OUT );
    }
    
    this.states.add( state );
  }
  
  void render( PGraphics canvas ){
    canvas.beginDraw();
    canvas.lights();
    canvas.clear();
    
    canvas.textFont( this.font );
    
    for ( int i = this.states.size() - 1; i >= 0; i-- ){
      State item = this.states.get( i );
      
      item.update();
      
      if ( item.finished() ){
        this.states.remove( i );
      }
    }
    
    int l = this.states.size();
    
    for ( int i = 0; i < l; i++ ){
      this.states.get( i ).render( canvas );
    }
    
    canvas.endDraw();
  }

  void setEffect( int effect ){
    for ( int i = this.states.size() - 1; i >= 0; i-- ){
      State item = this.states.get( i );
      item.setEffect( effect );
      item.update();
    }
  }

  void setFont( PFont font ){
    this.font = font;
  }
  
}