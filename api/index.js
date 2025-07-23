const express = require('express');
const app = express();
const port = 3000;

// Middleware to parse JSON
app.use(express.json());

// Default route
app.get('/', (req, res) => {
    res.send('Welcome to the rest API!');
});

// Start the server
app.listen(port, () => {
    console.log('Server running at http://localhost:${port}');
})


// GET all users
const users = [
    { id: 1, name: "John Doe", email: 'john@example.com'},
    { id: 2, name: 'Jane Smith', email: 'jane@example.com'}
];

app.get('/users', (req, res) => {
    res.json(users);
});

// GET a specific user
app.get('/users/:id', (req, res) => {
    const user = users.find(u => u.id === parseInt(req.params.id));
    if (!user) return res.status(404).send('User not found');
    res.json(user);
});

// POST a new user
app.post('/users', (req, res) => {
    const newUser = {
        id: users.length + 1,
        name: req.body.name,
        email: req.body.email
    };
    users.push(newUser);
    res.status(201).json(newUser);
});

// PUT to update a user
app.put('/users/:id', (req, res) => {
    const user = users.find(u => u.id === parseInt(req.params.id));
    if (!user) return res.status(404).send('User not found');

    user.name = req.body.name;
    user.email = req.body.email;
    res.json(user);
});

// DELETE a user
app.delete('/users/:id', (req, res) => {
    const index = users.findIndex(u => u.id === parseInt(req.params.id));
    if (index === -1) return res.status(404).send('User not found');

    users.splice(index, 1);
    res.send('User deleted');
})