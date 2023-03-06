let Rand = new brorand.Rand({getByte: () => 255});
let rand = Rand.rand;
let result= Rand.generate(16);

Rand = new brorand.Rand();
rand = Rand.rand;
result =  Rand.generate(1000);