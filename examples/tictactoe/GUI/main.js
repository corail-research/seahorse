$(document).ready(function () {
    var steps = [];
    var index = -1;
    const logElement = document.getElementById("log");
    const socket = io("ws://localhost:16001");
    socket.on("play", (...args) => {
        json = JSON.parse(args[0]);
            if (json.rep && json.rep.env){
                board = [] 
                for(var i=0;i<json.rep.dim[0];i++){
                  board.push([])
                  for (var _=0;_<json.rep.dim[1];_++)board[i].push('_')
                }
                for (const [key, value] of Object.entries(json.rep.env)) {
                  coord = key.replace(")","").replace("(","").replace(" ","").split(',')
                  board[coord[0]][coord[1]] = value.piece_type
                }
                steps.push(board);
                index = steps.length - 1;
                printBoard(board);
            }
            console.log(json)


        });
    
        const canvas = document.getElementById('canvas');
      
        // Define the grid size and cell size
        const gridSize = 3;
      
        // Function to draw the Tic Tac Toe grid
        function printBoard(gridData) {

      
          canvas.innerHTML = '<table id="table"><tr><td id="c0"></td><td id="c1"></td><td id="c2"></td></tr><tr><td id="c3"></td><td id="c4"></td><td id="c5"></td><tr><td id="c6"></td><td id="c7"></td><td id="c8"></td></tr></table>';
      
          if (gridData) {
            for (let row = 0; row < gridSize; row++) {
                for (let col = 0; col < gridSize; col++) {
                  const cellValue = gridData[row][col];
                  id = row*3+col
                  if (cellValue === 'X') {
                    drawElement("X",id)
                  } else if (cellValue === 'O') {
                    drawElement("O",id)
                  }
                  else{
                    document.getElementById("c"+id).classList.add("empty");
                    document.getElementById("c"+id).addEventListener("click", onCellClick);
              }
          }}
          
        }
      }

        function onCellClick(event) {
          if (event.target.classList.contains("empty")) {
            const cell = event.target;
            const cellId = cell.id.replace("c", "");

            socket.emit("interact", JSON.stringify({"position": cellId}));
          }}
      
        function drawElement(type, id) {
            // create a div
            var div = document.createElement("div");
            if (type == "X"){
              div.innerHTML = "&#x2715";
              div.style.color = "red";
            }
            else{
              div.innerHTML = "&#x25EF;";
              div.style.color = "blue";
            }
            document.getElementById("c"+id).appendChild(div);
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
