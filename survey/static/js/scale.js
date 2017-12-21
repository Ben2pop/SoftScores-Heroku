var getvalue = document.getElementById("enter");
var button = document.getElementById("send");
var count = document.createElement("div");
var classScale = document.getElementsByClassName("scale");
var checkbox = document.getElementsByClassName("checkbox");
var question = document.getElementsByClassName("tagged");
var test = document.getElementsByClassName("glyphicon glyphicon-asterisk")[0];
var check = document.getElementById("check");
try{var dict = JSON.parse(getvalue.value)}
catch(e) {dict = {}}


count.setAttribute("class", "numbers");

function peace(evt) {
    if(evt.checked == true){
        createScale(evt.name)
    }
    else {
        removeScale(evt.name)
    }
}

try{start()}
catch (e){}

function createScale(which){
    var index = parseInt(which);
    for(var i = 0; i <= 100; i++) {
        var strg = '<div class="numbers ' + i + ' ' + index + '"' +
            'onclick=\'select(this)\' data-toggle="tooltip" data-placement="top" title="' + i + '%"></div>';
        classScale[index].innerHTML += strg;
    }
}

function removeScale(which){
    var index = parseInt(which);
    var qnum = question[which].textContent;
    delete dict[qnum];
    classScale[index].innerHTML = "";
    getvalue.value = (JSON.stringify(dict))
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
    e.style.backgroundColor = "grey";
    var qnum = question[classvalue].textContent;
    dict[qnum] = mainvalue;
    getvalue.value = (JSON.stringify(dict))
}
function start() {
    var split = JSON.parse(getvalue.value);
    var keys = Object.keys(split);
    if(check.textContent != "choice-scale") {
        for (var q = 0; q < keys.length; q++) {
            for (var p = 0; p < question.length; p++) {
                if (keys[q] == question[p].textContent) {
                    var st = "numbers " + split[keys[q]] + " " + p;
                    document.getElementsByClassName(st)[0].style.backgroundColor = "grey"
                }
            }
        }
    }else{
        for(var q=0;q < keys.length; q++){
            checkbox[q].checked = true;
            createScale(q);
            for (var p = 0; p < question.length; p++) {
                if (keys[q] == question[p].textContent) {
                    var st = "numbers " + split[keys[q]] + " " + p;
                    document.getElementsByClassName(st)[0].style.backgroundColor = "grey"
                }
            }
        }
    }
}

button.onclick = function(){
    if(test != null){
        if(check.textContent != "choice-scale") {
            if (question.length == Object.keys(dict).length) {
                button.type = "submit"
            }
            else {
                test.innerText = "All fields are required!"
            }
        }
        else{
            if (Object.keys(dict).length >= 1) {
                button.type = "submit"
            }
            else {
                test.innerText = "All fields are required!"
            }
        }
    }
    else{
        button.type = "submit"
    }
};
