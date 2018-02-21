const exec = require('child_process').exec;
const cmd = 'handlebars ./handlebars_src --output=../static/bundle/handlbars.template.bundle.js'
var yourscript = exec(cmd,
        (error, stdout, stderr) => {
            console.log(`${stdout}`);
            console.log(`${stderr}`);
            if (error !== null) {
                console.log(`exec error: ${error}`);
            }
        });

