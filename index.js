const http = require("http");

const server = http.createServer((req, res) => {
  res.end("App chal raha hai 🚀");
});

server.listen(3000, () => {
  console.log("Server started");
});