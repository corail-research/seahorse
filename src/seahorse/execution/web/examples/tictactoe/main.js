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
            console.log(json)


        });
    
        const canvas = document.getElementById('canvas');

        // Get the canvas context
        const ctx = canvas.getContext('2d');
      
        // Define the grid size and cell size
        const gridSize = 3;
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
          
                  if (cellValue === 'X') {
                    drawX(row, col, markerSize);
                  } else if (cellValue === 'O') {
                    drawO(row, col, markerSize);
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
        function drawO(row, col, size) {
          ctx.strokeStyle = '#00f'; // Blue color
          ctx.lineWidth = 8;
      
          const x = col * cellSize + size;
          const y = row * cellSize + size;
      
          ctx.beginPath();
          ctx.arc(x, y, size - 10, 0, 2 * Math.PI);
          ctx.stroke();
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
