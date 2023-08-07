$(document).ready(function () {
    var steps = [];
    var index = -1;
    const logElement = document.getElementById("log");
    const socket = io("ws://localhost:8080");
    socket.on("play", (...args) => {
        json = JSON.parse(args[0]);
            if (json.rep && json.rep.board){
                steps.push(json.rep.board);
                index = steps.length - 1;
                printBoard(json.rep.board);
            }


        });
    
        const canvas = document.getElementById('canvas');

        // Get the canvas context
        const ctx = canvas.getContext('2d');
      
        // Define the grid size and cell size
        const gridSize = 9;
        const cellSize = canvas.width / gridSize;
      
        // Function to draw the Tic Tac Toe grid
        function printBoard(gridData) {
          // Clear the canvas
          ctx.clearRect(0, 0, canvas.width, canvas.height);
      
          // Draw the grid lines
          ctx.strokeStyle = '#000'; // Black color
          ctx.lineWidth = 2;
      
          for (let i = 1; i < gridSize; i++) {
            // Draw vertical lines
            ctx.beginPath();
            ctx.moveTo(i * cellSize, 0);
            ctx.lineTo(i * cellSize, canvas.height);
            ctx.stroke();
      
            // Draw horizontal lines
            ctx.beginPath();
            ctx.moveTo(0, i * cellSize);
            ctx.lineTo(canvas.width, i * cellSize);
            ctx.stroke();
          }
      
          // Draw the X and O markers
          const markerSize = cellSize / 2;
          if (gridData) {
            for (let row = 0; row < gridSize; row++) {
                for (let col = 0; col < gridSize; col++) {
                  const cellValue = gridData[row][col];
                  if (cellValue) {
                    if (cellValue[1] === 'R') {
                      drawO_red(row, col, markerSize,cellValue);
                    } else if (cellValue[1] === 'Y') {
                      drawO_yellow(row, col, markerSize,cellValue);
                    } 
                  }
                }
              }
          }
          
        }
      
        function drawX(row, col, size) {
            ctx.strokeStyle = '#f00'; // Red color
            ctx.lineWidth = 8;
          
            const x = col * cellSize + size;
            const y = row * cellSize + size;
          
            const offset = 10; // Adjust the offset as needed
          
            ctx.beginPath();
            ctx.moveTo(x - size + offset, y - size + offset);
            ctx.lineTo(x + size - offset, y + size - offset);
            ctx.moveTo(x - size + offset, y + size - offset);
            ctx.lineTo(x + size - offset, y - size + offset);
            ctx.stroke();
          }
      
        // Function to draw an O marker
        function drawO_yellow(row, col, size, cell) {
          ctx.strokeStyle = '#FFFF00'; // yellow
          ctx.lineWidth = 8;
      
          const x = col * cellSize + size;
          const y = row * cellSize + size;
      
          ctx.beginPath();
          ctx.arc(x, y, size - 10, 0, 2 * Math.PI);
          ctx.fillStyle = "#808080";
          ctx.stroke();
          ctx.font = `${size - 10}px Arial`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(cell[2], x, y);
          ctx.stroke();
        }

        // Function to draw an O marker
        function drawO_red(row, col, size, cell) {
          ctx.strokeStyle = '#FF0000'; // red
          ctx.lineWidth = 8;
      
          const x = col * cellSize + size;
          const y = row * cellSize + size;
      
          ctx.beginPath();
          ctx.arc(x, y, size - 10, 0, 2 * Math.PI);
          ctx.fillStyle = "#808080";
          ctx.stroke();
          ctx.font = `${size - 10}px Arial`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(cell[2], x, y);
        }
      

    $("#next").click(function () {
        if (index < steps.length-1){
            
            index++;
            printBoard(steps[index]);
        }
    });

    $("#previous").click(function () {
        if (index > 0){
            index--;
            printBoard(steps[index]);
        }
    });

    printBoard(null);
    });