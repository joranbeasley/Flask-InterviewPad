class simple_wsio{
    private io:any=null;
    connected:boolean=false;
    connect(uri,opts){
        console.log("CONNECT:",uri,opts)
        console.log("WINDOW[io]:",window['io'])
        this.connected = true;

    }
    on($eventType:string,$callBack:Function){
        this.io.on($eventType,$callBack)
    };
    emit($eventType,$payload){
        this.io.emit($eventType,$payload)
    }
}
export class IP_WebSocketIO{
    private socket;
    constructor(){
        this.socket = null;
    }
    on($eventType:string,$callBack:Function){
        this.socket.on($eventType,$callBack)
    }
}