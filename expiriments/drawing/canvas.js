// DOM vars
let drawForm = document.querySelector("#draw");
let clearBtn = document.querySelector("#clear");

// vars
//drawMode[0]: boolean : mouseDown
//drawMode[1]: 0: none, 1: brush, 2: eraser, 3: bucket
let drawMode = [false, 0];
// Brush color
let brColor = [255, 200, 100];
// Background color
let bgColor = 240;
// Precedent point (last frame)
let precPt = [];

// DOM handlers
// Radio buttons
drawForm.addEventListener("change", () => {
  for (let ch of drawForm.children) {
    if (ch.localName == "input" && ch.checked) {
      drawMode[1] = Number(ch.value);
      precPt = [];
    };
  }
});
drawForm.dispatchEvent(new Event("change"));

// Clear
clearBtn.addEventListener("click", e => {
  e.preventDefault();
  background(240);
  console.log("clear");
});

function setup() {
  createCanvas(800, 800);
  canvas.style.border = "1px solid black";
  canvas.style.margin = "10px";

  strokeWeight(10);
  background(240);
}

function draw() {
  if (drawMode[0]) {
    if (drawMode[1] == 1 || drawMode[1] == 2) {
      let precPtChanged = (precPt[0] != mouseX || precPt[1] != mouseY);
      let chColor = drawMode[1] == 1 ? brColor : bgColor;

      if (precPt[0] && precPtChanged) {
        noFill();
        stroke(chColor);
        console.log(`line of color ${chColor} from ${precPt[0]}, ${precPt[1]} to ${mouseX}, ${mouseY}`);
        line(precPt[0], precPt[1], mouseX, mouseY);
      }

      if (!precPt[0] || precPtChanged) {
        noStroke();
        fill(chColor);
        ellipse(mouseX, mouseY, 10, 10);
        precPt = [mouseX, mouseY];
      }
    }
  }
}

function mouseDown() {
  if (drawMode[1] == 3) {
    console.log(`fill of color ${brColor} at ${mouseX}, ${mouseY}`);
  }
  drawMode[0] = true;
}

function mouseUp() {
  drawMode[0] = false;
  precPt = [];
}