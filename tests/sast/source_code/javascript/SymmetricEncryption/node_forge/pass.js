var forge = require('node-forge');
var cipher = forge.cipher.createCipher('AES-CBC', key);
cipher.start({iv: iv});
