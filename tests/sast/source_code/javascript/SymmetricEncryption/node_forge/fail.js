var forge = require('node-forge');
var cipher = forge.cipher.createCipher('DES-CBC', key);
cipher.start({iv: iv});
/* alternatively, generate a password-based 16-byte key
var salt = forge.random.getBytesSync(128);
var key = forge.pkcs5.pbkdf2('password', salt, numIterations, 16);
*/