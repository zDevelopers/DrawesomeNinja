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
  //console.log("clear");
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
        //console.log(`line of color ${chColor} from ${precPoint[0]}, ${precPoint[1]} to ${mouseX}, ${mouseY}`);
        line(precPoint[0], precPoint[1], mouseX, mouseY);
      }

      if (!precPoint[0] || precPointChanged) {
        noStroke();
        fill(chColor);
        strokeWeight(chWeight);
        ellipse(mouseX, mouseY, chWeight, chWeight);
        precPoint = [mouseX, mouseY];
      }
    }
  }
}

function bucketFill(startX, startY) {
  let ctxData = ctx.getImageData(0, 0, width, height);
  let startPos = (startY * width + startY) * 4;
  let [startR, startG, startB] = ctxData.data.subarray(startPos, startPos + 3);
  let pixelStack = [[startX, startY]];
  
  while (pixelStack.length) {
    let [x, y] = pixelStack.pop();
    let pixelPos = (y * width + x) * 4;

    while (y-- >= 0 && matchStartColor(pixelPos)) {
      pixelPos -= width * 4;
    }
    pixelPos += width * 4;

    ++y;
    let reachLeft = false, reachRight = false;

    while (y++ < height - 1 && matchStartColor(pixelPos)) {
      colorPixel(pixelPos);
      
      if (x > 0) {
        if (matchStartColor(pixelPos - 4)) {
          if (!reachLeft) {
            pixelStack.push([x - 1, y]);
            reachLeft = true;
          }
        }
        else if (reachLeft) reachLeft = false;
      }
  	
      if (x < width - 1) {
        if (matchStartColor(pixelPos + 4)) {
          if (!reachRight) {
            pixelStack.push([x + 1, y]);
            reachRight = true;
          }
        }
        else if (reachRight) reachRight = false;
      }
  			
      pixelPos += width * 4;
    }
  }
  
  ctx.putImageData(ctxData, 0, 0);
    
  function matchStartColor(pixelPos) {
    let r = ctxData.data[pixelPos];
    let g = ctxData.data[pixelPos + 1];
    let b = ctxData.data[pixelPos + 2];

    return (Math.abs(r - startR) < 5
      && Math.abs(g - startG < 5)
      && Math.abs(b - startB < 5)
    );
  }
  
  function colorPixel(pixelPos) {
    ctxData.data[pixelPos] = brushColor[0];
    ctxData.data[pixelPos + 1] = brushColor[1];
    ctxData.data[pixelPos + 2] = brushColor[2];
    ctxData.data[pixelPos + 3] = 255;
  }
}

function mouseDown() {
  if (drawMode == 3) {
    //console.log(`fill of color ${brColor} at ${mouseX}, ${mouseY}`);
    bucketFill(mouseX, mouseY);
  }
}

function mouseUp() {
  precPoint = [];
}
