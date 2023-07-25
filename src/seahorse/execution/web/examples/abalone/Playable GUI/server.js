const WebSocket = require('ws');

const wss = new WebSocket.Server({ noServer: true });

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.on('message', (message) => {
    const decodedMessage = Buffer.from(message).toString('utf-8');
    console.log('Received message from Python client:', decodedMessage);

    // Send the message to all connected HTML/JS clients
    wss.clients.forEach((client) => {
      if (client != ws && client.readyState === WebSocket.OPEN) {
        client.send(decodedMessage);
      }
    });
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

const httpServer = require('http').createServer();

httpServer.on('upgrade', (request, socket, head) => {
  wss.handleUpgrade(request, socket, head, (ws) => {
    wss.emit('connection', ws, request);
  });
});

httpServer.listen(8080, () => {
  console.log('WebSocket server started on port 8080');
});