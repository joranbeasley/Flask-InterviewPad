function MySocketIO(ws_url,userCredentials,options){
    var self=this;
    self.socket = io.connect(ws_url,options);
    self.editor = null;
    self.chat_panel = null;
    this.emit=function(eventType,payload){
        console.log("emit:",eventType,payload)
        self.socket.emit(eventType,payload)
    };
    this.on=function(eventType,callback){
        self.socket.on(eventType,callback)
    };

    self.on("connect", function(data) {
        console.log("Connected!~~",data)
        self.emit("join_room",userCredentials)
    });
    self.on("error", function(data){
        console.log("GOT ERROR MSG FROM WS:",data)
    })
    return this;
}