var getvalue = document.getElementById("enter");
console.log(234);
var button = document.getElementById("send");
var count = document.createElement("div");
var classScale = document.getElementsByClassName("scale");
var question = document.getElementsByClassName("tagged");
var test = document.getElementsByClassName("glyphicon glyphicon-asterisk")[0];
try{var dict = JSON.parse(getvalue.value)}
catch(e) {dict = {}}
console.log(234);
count.setAttribute("class", "numbers");

var my = document.getElementsByClassName("scale");
for(var k = 0; k < my.length; k++){
    for(var i = 0; i <= 100; i++) {
        var strg = '<div class="numbers ' + i + ' ' + k + '"' +
            'onclick=\'select(this)\' data-toggle="tooltip" title= "' + i + '%" ></div>';
        my[k].innerHTML += strg;
    }
}
try{start()}
catch (e){}
function start() {
    var split = JSON.parse(getvalue.value);
    var keys = Object.keys(split);
    for(var q = 0; q<keys.length; q++){
        for (var p = 0; p<question.length; p++){
            if(keys[q] == question[p].textContent){
                var st = "numbers " + split[keys[q]] + " " + p;
                document.getElementsByClassName(st)[0].style.backgroundColor = "red"
            }
        }
    }
}
function select(e) {
    var mainvalue = parseInt(e.className.split(" ")[1]);
    var classvalue = parseInt(e.className.split(" ")[2]);
    var num = classScale.length;
    var p = e.parentNode;
    var c = p.children;
    for(var r = 0; r<c.length;r++){
        c[r].style.backgroundColor = "green";
    }
    e.style.backgroundColor = "red";
    var qnum = question[classvalue].textContent;
    dict[qnum] = mainvalue;
    getvalue.value = (JSON.stringify(dict))
}
button.onclick = function () {
    if(test != null){
        if(question.length == Object.keys(dict).length){
            button.type = "submit"
        }
        else{
            test.innerText = "All fields are required!"
        }
    }
    else{
        button.type = "submit"
    }
};
