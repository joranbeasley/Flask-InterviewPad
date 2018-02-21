Handlebars.registerHelper('isEqual', function(lvalue, rvalue, options) {
        if (arguments.length < 3)
            console.log("AAA",arguments,"BBB")
            // throw new Error("Handlebars Helper isEqual needs 2 parameters");
        else if( lvalue!=rvalue ) {
            return options.inverse(this);
        } else {
            return options.fn(this);
        }
    })