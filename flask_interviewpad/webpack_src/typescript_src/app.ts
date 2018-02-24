// Revisit this later i think ... for now we will just use js
// import ace from "@types/ace"
class user{
    email:string;
    state:string;
    is_active:boolean;
    url:string;
    invite_expires:Date;
    user_color:string;
    nickname:string;
    get username():string{
        return this.nickname;
    }
    set username(value:string){
        this.nickname = value;
    }
}
class room{
    room_name:string;
    users:user[];
    user_went_afk(userDetails){

    }
    user_came_back(userDetails){

    }
    user_joined(userDetails){

    }
    user_left(userDetails){

    }
}
class MySocketIO{

}
class MyAceEditor{
    private editor:any;
    constructor(divId:string){
        document.getElementById(divId)
        this.editor = window['ace'].edit(divId,true)
    }
}
class MyChatPanel{

}
class MyProblemStatement{

}
class AppHeader{

}
class AppBody{

}
class AppFooter{

}
export class app{
    room:room;
    user:user;
    socket:MySocketIO;
    elements:{ace: MyAceEditor,chat: MyChatPanel,active_problem:MyProblemStatement};

    constructor(){
        this.elements.ace = new MyAceEditor("editor");
    }
}