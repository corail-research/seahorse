$(document).ready(function () {
  var steps = [];
  var index = -1;
  const logElement = document.getElementById("log");
  var play = false;
  const socket = io("ws://10.200.37.65:16001");
  socket.on("play", (...args) => {
    json = JSON.parse(args[0]);
    //console.log(json);
    if (json.rep && json.rep.board) {
      convertedGrid = convertToGridData({"board":json.rep.board, "scores":json.scores});
      steps.push(convertedGrid);
      index = steps.length - 1;
      drawGrid(convertedGrid);
    }
  });

  socket.on("disconnect", (...args) => {
    // set display block to img of id #img

    //$("#img").css("display", "block");
  });

  $("#play").click(function () {
    play = true;
    var loop = setInterval(function () {
      if (play) {
        if (index < steps.length - 1) {
          index++;
          drawGrid(steps[index]);
        } else {  
          play = false;
          clearInterval(loop);
        }
      }else{
        clearInterval(loop);
      }
    }, $("#time").val());

  });

  $("#stop").click(function () {
    play = false;
  });

  $("#reset").click(function () {
    index = 0;
    drawGrid(steps[index]);
  });

  const canvas = document.getElementById("canvas");

  // Get the canvas context
  const ctx = canvas.getContext("2d");

  function get_id_color(color, grid){
    for (i = 0; i < grid.length; i++) {
      for (j = 0; j < grid[i].length; j++) {
        if(grid[i][j] && grid[i][j][1] == color) {
          return grid[i][j][0];
        }
      }
    }
    console.log("ERROR: No color found");
  }

  

  function drawGrid(gridData) {

    //console.log(gridData);

    scores = gridData["scores"];
    gridData = gridData["gridData"];

    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  
    ctx.fillStyle = "lightgray";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  
    // Calculate the available width and height for the grid
    const canvasWidth = canvas.clientWidth;
    const canvasHeight = canvas.clientHeight;
  
    const gridSize = 9;
    const cellSize = Math.min(canvasWidth, canvasHeight) / gridSize;
  
    // Calculate the horizontal and vertical offset to center the grid
    const gridWidth = gridSize * cellSize;
    const gridHeight = gridSize * cellSize;
    const offsetX = (canvasWidth - gridWidth) / 2 + 125;
    const offsetY = (canvasHeight - gridHeight) / 2;
  
    // Define the grid data with the initial Abalone state
    
  
    // Define hexagon radius and spacing
    const hexagonRadius = cellSize / 2.5;
    const spacing = cellSize * 0.7;
  
    // Calculate the vertical offset to move the grid downwards
    const marginTop = hexagonRadius * 4;


  
    for (let row = 0; row < gridData.length; row++) {
      for (let col = 0; col < gridData[row].length; col++) {
        let x = col * spacing + hexagonRadius + offsetX;
        let y = row * spacing * 0.85 + hexagonRadius + marginTop + offsetY;
  
        // Adjust x coordinate for odd rows
        if (row % 2 !== 0) {
          x += spacing / 2;
        }
  
        const value = gridData[row][col];
  
        // Draw hexagon border for values different from 0
        if (value !== 0) {
          ctx.strokeStyle = "black";
          ctx.lineWidth = 2;
          ctx.beginPath();
          for (let side = 0; side < 6; side++) {
            const angle = ((60 * side - 30) * Math.PI) / 180; // Adjust the rotation angle
            const cx = x + hexagonRadius * Math.cos(angle);
            const cy = y + hexagonRadius * Math.sin(angle);
            ctx.lineTo(cx, cy);
          }
          ctx.closePath();
          ctx.stroke();
  
          // Draw circle inside the hexagon
          if (value !== 3) {
            ctx.fillStyle = value === 1 ? "black" : "white";
            ctx.beginPath();
            ctx.arc(x, y, hexagonRadius / 1.5, 0, 2 * Math.PI);
            ctx.closePath();
            ctx.fill();
          }
        }
      }
    }

    const blackCircles = scores['B'] || 0;
  for (let i = 0; i < blackCircles; i++) {
    console.log("black");
    const cx = hexagonRadius * (2*i + 2);
    const cy = canvas.height - hexagonRadius*2;
    ctx.fillStyle = 'black';
    ctx.beginPath();
    ctx.arc(cx, cy, hexagonRadius / 1.5, 0, 2 * Math.PI);
    ctx.closePath();
    ctx.fill();
  }

  // Draw the bottom right white circles
  const whiteCircles = scores['W'] || 0;
  for (let i = 0; i < whiteCircles; i++) {
    console.log("white");
    const cx = canvas.width - hexagonRadius * (2*i + 2);
    const cy = canvas.height - hexagonRadius*2;
    ctx.fillStyle = 'white';
    ctx.beginPath();
    ctx.arc(cx, cy, hexagonRadius / 1.5, 0, 2 * Math.PI);
    ctx.closePath();
    ctx.fill();
  }


  }

  $("#next").click(function () {
    if (index < steps.length - 1) {
      index++;
      console.log(index);
      drawGrid(steps[index]);
    }
  });

  $("#previous").click(function () {
    if (index > 0) {
      index--;
      console.log(index);
      drawGrid(steps[index]);
    }
  });

  function convertToGridData(board) {
    //console.log(board); 
    scores = board["scores"]
    board = board["board"]

    conversion = {'0_4': [0, 6], '1_3': [0, 5], '2_2': [0, 4], '3_1': [0, 3], '4_0': [0, 2], '1_5': [1, 6], '2_4': [1, 5], '3_3': [1, 4], '4_2': [1, 3], '5_1': [1, 2], '6_0': [1, 1], '2_6': [2, 7], '3_5': [2, 6], '4_4': [2, 5], '5_3': [2, 4], '6_2': [2, 3], '7_1': [2, 2], '8_0': [2, 1], '3_7': [3, 7], '4_6': [3, 6], '5_5': [3, 5], '6_4': [3, 4], '7_3': [3, 3], '8_2': [3, 2], '9_1': [3, 1], '10_0': [3, 0], '4_8': [4, 8], '5_7': [4, 7], '6_6': [4, 6], '7_5': [4, 5], '8_4': [4, 4], '9_3': [4, 3], '10_2': [4, 2], '11_1': [4, 1], '12_0': [4, 0], '6_8': [5, 7], '7_7': [5, 6], '8_6': [5, 5], '9_5': [5, 4], '10_4': [5, 3], '11_3': [5, 2], '12_2': [5, 1], '13_1': [5, 0], '8_8': [6, 7], '9_7': [6, 6], '10_6': [6, 5], '11_5': [6, 4], '12_4': [6, 3], '13_3': [6, 2], '14_2': [6, 1], '10_8': [7, 6], '11_7': [7, 5], '12_6': [7, 4], '13_5': [7, 3], '14_4': [7, 2], '15_3': [7, 1], '12_8': [8, 6], '13_7': [8, 5], '14_6': [8, 4], '15_5': [8, 3], '16_4': [8, 2]}

    //console.log(get_id_color("B",board));
    //real_scores = {"W":scores[get_id_color("W",board)]*-1, "B":scores[get_id_color("B",board)]*-1}
    real_scores = {"W":0, "B":0}
    //console.log(real_scores);

    const gridData = [
      [0, 0, 3, 3, 3, 3, 3, 0, 0],
      [0, 3, 3, 3, 3, 3, 3, 0, 0],
      [0, 3, 3, 3, 3, 3, 3, 3, 0],
      [3, 3, 3, 3, 3, 3, 3, 3, 0],
      [3, 3, 3, 3, 3, 3, 3, 3, 3],
      [3, 3, 3, 3, 3, 3, 3, 3, 0],
      [0, 3, 3, 3, 3, 3, 3, 3, 0],
      [0, 3, 3, 3, 3, 3, 3, 0, 0],
      [0, 0, 3, 3, 3, 3, 3, 0, 0],
    ];
    for (let key in board) {
      new_key = key.substring(1, key.length - 1).replace(/, /g, "_");
      obj = JSON.parse(board[key]);
      let new_coord = conversion[new_key];
      gridData[new_coord[0]][new_coord[1]] = obj["piece_type"]
    }
    /*
    gridData[0][6] = board[0][4] ?  board[0][4][1]: 3;
    gridData[0][5] = board[1][3] ?  board[1][3][1]: 3;
    gridData[0][4] = board[2][2] ?  board[2][2][1]: 3;
    gridData[0][3] = board[3][1] ?  board[3][1][1]: 3;
    gridData[0][2] = board[4][0] ?  board[4][0][1]: 3;

    gridData[1][6] = board[1][5] ?  board[1][5][1]: 3;
    gridData[1][5] = board[2][4] ?  board[2][4][1]: 3;
    gridData[1][4] = board[3][3] ?  board[3][3][1]: 3;
    gridData[1][3] = board[4][2] ?  board[4][2][1]: 3;
    gridData[1][2] = board[5][1] ?  board[5][1][1]: 3;
    gridData[1][1] = board[6][0] ?  board[6][0][1]: 3;

    gridData[2][7] = board[2][6] ?  board[2][6][1]: 3;
    gridData[2][6] = board[3][5] ?  board[3][5][1]: 3;
    gridData[2][5] = board[4][4] ?  board[4][4][1]: 3;
    gridData[2][4] = board[5][3] ?  board[5][3][1]: 3;
    gridData[2][3] = board[6][2] ?  board[6][2][1]: 3;
    gridData[2][2] = board[7][1] ?  board[7][1][1]: 3;
    gridData[2][1] = board[8][0] ?  board[8][0][1]: 3;

    gridData[3][7] = board[3][7] ?  board[3][7][1]: 3;
    gridData[3][6] = board[4][6] ?  board[4][6][1]: 3;
    gridData[3][5] = board[5][5] ?  board[5][5][1]: 3;
    gridData[3][4] = board[6][4] ?  board[6][4][1]: 3;
    gridData[3][3] = board[7][3] ?  board[7][3][1]: 3;
    gridData[3][2] = board[8][2] ?  board[8][2][1]: 3;
    gridData[3][1] = board[9][1] ?  board[9][1][1]: 3;
    gridData[3][0] = board[10][0] ?  board[10][0][1]: 3;

    gridData[4][8] = board[4][8] ?  board[4][8][1]: 3;
    gridData[4][7] = board[5][7] ?  board[5][7][1]: 3;
    gridData[4][6] = board[6][6] ?  board[6][6][1]: 3;
    gridData[4][5] = board[7][5] ?  board[7][5][1]: 3;
    gridData[4][4] = board[8][4] ?  board[8][4][1]: 3;
    gridData[4][3] = board[9][3] ?  board[9][3][1]: 3;
    gridData[4][2] = board[10][2] ?  board[10][2][1]: 3;
    gridData[4][1] = board[11][1] ?  board[11][1][1]: 3;
    gridData[4][0] = board[12][0] ?  board[12][0][1]: 3;

    gridData[5][7] = board[6][8] ?  board[6][8][1]: 3;
    gridData[5][6] = board[7][7] ?  board[7][7][1]: 3;
    gridData[5][5] = board[8][6] ?  board[8][6][1]: 3;
    gridData[5][4] = board[9][5] ?  board[9][5][1]: 3;
    gridData[5][3] = board[10][4] ?  board[10][4][1]: 3;
    gridData[5][2] = board[11][3] ?  board[11][3][1]: 3;
    gridData[5][1] = board[12][2] ?  board[12][2][1]: 3;
    gridData[5][0] = board[13][1] ?  board[13][1][1]: 3;

    gridData[6][7] = board[8][8] ?  board[8][8][1]: 3;
    gridData[6][6] = board[9][7] ?  board[9][7][1]: 3;
    gridData[6][5] = board[10][6] ?  board[10][6][1]: 3;
    gridData[6][4] = board[11][5] ?  board[11][5][1]: 3;
    gridData[6][3] = board[12][4] ?  board[12][4][1]: 3;
    gridData[6][2] = board[13][3] ?  board[13][3][1]: 3;
    gridData[6][1] = board[14][2] ?  board[14][2][1]: 3;

    gridData[7][6] = board[10][8] ?  board[10][8][1]: 3;
    gridData[7][5] = board[11][7] ?  board[11][7][1]: 3;
    gridData[7][4] = board[12][6] ?  board[12][6][1]: 3;
    gridData[7][3] = board[13][5] ?  board[13][5][1]: 3;
    gridData[7][2] = board[14][4] ?  board[14][4][1]: 3;
    gridData[7][1] = board[15][3] ?  board[15][3][1]: 3;

    gridData[8][6] = board[12][8] ?  board[12][8][1]: 3;
    gridData[8][5] = board[13][7] ?  board[13][7][1]: 3;
    gridData[8][4] = board[14][6] ?  board[14][6][1]: 3;
    gridData[8][3] = board[15][5] ?  board[15][5][1]: 3;
    gridData[8][2] = board[16][4] ?  board[16][4][1]: 3;
    */
    for(i = 0; i < 9; i++) {
      for(j = 0; j < 9; j++) {
        if(gridData[i][j] == "W") {
          gridData[i][j] = 2;
        } else if(gridData[i][j] == "B") {
          gridData[i][j] = 1;
        }
      }
    }
    return {"gridData":gridData, "scores":real_scores};
  }
  
  function resizeCanvas() {

    defaultGridData = {"gridData":[
      [0, 0, 2, 2, 2, 2, 2, 0, 0],
      [0, 2, 2, 2, 2, 2, 2, 0, 0],
      [0, 3, 3, 2, 2, 2, 3, 3, 0],
      [3, 3, 3, 3, 3, 3, 3, 3, 0],
      [3, 3, 3, 3, 3, 3, 3, 3, 3],
      [3, 3, 3, 3, 3, 3, 3, 3, 0],
      [0, 3, 3, 1, 1, 1, 3, 3, 0],
      [0, 1, 1, 1, 1, 1, 1, 0, 0],
      [0, 0, 1, 1, 1, 1, 1, 0, 0],
    ], "scores":{"W":0, "B":0}};
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    drawGrid(steps[index] || defaultGridData);
  }

  // Resize canvas when the window is resized
  window.addEventListener("resize", resizeCanvas);

  // Initial canvas setup
  resizeCanvas();
});
