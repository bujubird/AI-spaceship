const express = require('express');
const app = express();
const http = require('http');
const server = http.createServer(app);
const { Server } = require("socket.io");
const io = new Server(server);
const path = require('path');

app.use(express.static(__dirname));

// Game State
const rooms = {}; // roomId -> { host: socketId, client: socketId, state: {} }

io.on('connection', (socket) => {
    console.log('A user connected:', socket.id);

    // Listens for 'JoinGame' or 'HostGame'
    // For simplicity, we'll just have one global "game" or allow users to specify room?
    // User requirement: "allow another student can connect into your screen through their local area network"
    // So one acts as Host, one as Client. They probably need to find each other.
    // We can implement a simple "Host" button that creates a room, and "Join" that lists rooms or joins by IP (but browser context makes IP scanning hard).
    // Let's use a simple Room ID system or just a single lobby for simplicity in a classroom LAN.
    // Actually, "connect to another host" implies explicit connection.
    // Let's allow users to enter a Room ID (e.g. Host IP or just a name).
    
    socket.on('host_game', (roomId) => {
        if (rooms[roomId]) {
            socket.emit('error_msg', 'Room already exists');
            return;
        }
        rooms[roomId] = { host: socket.id, client: null };
        socket.join(roomId);
        socket.emit('hosting_started', roomId);
        console.log(`Room ${roomId} created by ${socket.id}`);
    });

    socket.on('join_game', (roomId) => {
        const room = rooms[roomId];
        if (!room) {
            socket.emit('error_msg', 'Room not found');
            return;
        }
        if (room.client) {
            socket.emit('error_msg', 'Room full');
            return;
        }
        room.client = socket.id;
        socket.join(roomId);
        
        // Notify Host that client joined
        io.to(room.host).emit('client_connected', socket.id);
        socket.emit('connected_to_host', roomId);
        console.log(`${socket.id} joined room ${roomId}`);
    });

    // --- RELAY MESSAGES ---
    // We forward messages to the other peer in the room.

    const forwardToPeer = (msgType, data) => {
        // Find room this socket is in
        // (Expensive search but okay for small scale)
        for (const [rid, r] of Object.entries(rooms)) {
            if (r.host === socket.id) {
                if (r.client) io.to(r.client).emit(msgType, data);
                return;
            }
            if (r.client === socket.id) {
                io.to(r.host).emit(msgType, data);
                return;
            }
        }
    };

    // Client -> Host
    socket.on('client_hello', (data) => forwardToPeer('client_hello', data));
    socket.on('client_ship_move', (data) => forwardToPeer('client_ship_move', data));
    
    // Host -> Client
    socket.on('server_screen_config', (data) => forwardToPeer('server_screen_config', data));
    socket.on('entity_move', (data) => forwardToPeer('entity_move', data)); // Batch or single?
    socket.on('entity_create', (data) => forwardToPeer('entity_create', data));
    socket.on('entity_delete', (data) => forwardToPeer('entity_delete', data));
    socket.on('damage_event', (data) => forwardToPeer('damage_event', data));
    
    // Both Directions
    socket.on('ship_sprite', (data) => forwardToPeer('ship_sprite', data));
    socket.on('weapon_fired', (data) => forwardToPeer('weapon_fired', data));

    socket.on('disconnect', () => {
        console.log('User disconnected:', socket.id);
        for (const [rid, r] of Object.entries(rooms)) {
            if (r.host === socket.id) {
                // Host left, room dead
                if (r.client) io.to(r.client).emit('host_disconnected');
                delete rooms[rid];
            } else if (r.client === socket.id) {
                // Client left
                io.to(r.host).emit('client_disconnected');
                r.client = null;
            }
        }
    });
});

const PORT = 3000;
server.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
