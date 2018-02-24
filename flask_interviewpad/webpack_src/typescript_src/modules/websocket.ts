class WebSocketIO{
    private io:any=null;
    connected:boolean=false;
    connect(uri,opts){
        this.io = window['io'](uri,opts)
        this.connected = true;

    }
    on($eventType:string,$callBack:Function){
        this.io.on($eventType,$callBack)
    };
    emit($eventType,$payload){
        this.io.emit($eventType,$payload)
    }
}
export class SimpleWebsocket{
    private socket:WebSocketIO;
    constructor(){
        this.socket = new WebSocketIO();
    }
    emit($eventType,$payload){
        this.socket.emit($eventType,$payload)
    }
    on($eventType:string,$callBack:Function){
        this.socket.on($eventType,$callBack)
    }
}