"use strict";

function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

function multiply(a, b) {
    return a * b;
}

function divide(a, b) {
    return a / b;
}

function main() {
    let x = 10;
    let y = 5;
    console.log(`${x} + ${y} = ${add(x, y)}`);
    console.log(`${x} - ${y} = ${subtract(x, y)}`);
    console.log(`${x} * ${y} = ${multiply(x, y)}`);
    console.log(`${x} / ${y} = ${divide(x, y)}`);
}


main();