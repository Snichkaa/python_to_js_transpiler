"use strict";

function range() {
    const args = Array.from(arguments);
    let start = 0, stop = 0, step = 1;
    if (args.length === 1) {
        stop = args[0];
    } else if (args.length === 2) {
        start = args[0]; stop = args[1];
    } else if (args.length >= 3) {
        start = args[0]; stop = args[1]; step = args[2];
    }
    if (step === 0) { throw new Error("range() step argument must not be zero"); }
    const out = [];
    if (step > 0) {
        for (let i = start; i < stop; i += step) out.push(i);
    } else {
        for (let i = start; i > stop; i += step) out.push(i);
    }
    return out;
}

function fibonacci(n) {
    if (n <= 1) {
        return n;
    } else {
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
}

function main() {
    for (let i of range(10)) {
        console.log(`fib(${i}) = ${fibonacci(i)}`);
    }
}


main();