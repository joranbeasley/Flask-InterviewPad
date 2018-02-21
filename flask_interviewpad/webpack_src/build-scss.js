const exec = require('child_process').exec;
let x = process.argv.splice(0,2)
console.log(process.argv)
console.log(x)
const cmd = 'node-sass '+process.argv.join(" ")
console.log("RUN:",cmd)
var yourscript = exec(cmd,
        (error, stdout, stderr) => {
            console.log(`${stdout}`);
            console.log(`${stderr}`);
            if (error !== null) {
                console.log(`exec error: ${error}`);
            }
        });

