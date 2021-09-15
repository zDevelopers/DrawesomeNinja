let drawForm = document.querySelector("#draw");
let clearBtn = document.querySelector("#clear");

// 0: none, 1: brush, 2: eraser, 3: bucket
let drawMode = 0;
let brushColor = [255, 200, 100];
let bgColor = 240;
let precPoint = [];

// Radio buttons
function formOnChange() {
  for (let ch of drawForm.children) {
    if (ch.localName == "input" && ch.checked) {
      drawMode = Number(ch.value);
      precPoint = [];
    }
  }
}

drawForm.addEventListener("change", formOnChange);
formOnChange();

// Clear
clearBtn.addEventListener("click", e => {
  e.preventDefault();
  background(240);
  console.log("clear");
});

function setup() {
  // w, h
  createCanvas(800, 800);
  canvas.style.border = "1px solid black";
  canvas.style.margin = "10px";

  background(240);
}

function draw() {
  if (mouseIsDown) {
    if (drawMode == 1 || drawMode == 2) {
      let precPointChanged = (precPoint[0] != mouseX || precPoint[1] != mouseY);
      let chColor = drawMode == 1 ? brushColor : bgColor;
      let chWeight = drawMode == 1 ? 10 : 20;

      if (precPoint[0] && precPointChanged) {
        noFill();
        strokeWeight(chWeight);
        stroke(chColor);
        console.log(`line of color ${chColor} from ${precPoint[0]}, ${precPoint[1]} to ${mouseX}, ${mouseY}`);
        line(precPoint[0], precPoint[1], mouseX, mouseY);
      }

      if (!precPoint[0] || precPointChanged) {
        noStroke();
        fill(chColor);
        strokeWeight(chWeight);
        ellipse(mouseX, mouseY, 10, 10);
        precPoint = [mouseX, mouseY];
      }
    }
  }
}

function mouseDown() {
  if (drawMode == 3) {
    console.log(`fill of color ${brColor} at ${mouseX}, ${mouseY}`);
  }
}

function mouseUp() {
  precPoint = [];
}
