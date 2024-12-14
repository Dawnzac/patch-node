## Patch-node

#### A spin-off on open source remote patch management

_For linux systems only_

- run server.py (python3 server.py) (flask necessary)
- Copy the genertated link and run it on client systems
- reports will be logged in agent_reports.log in the same directory

Use Postman or relevent options to send API requests

- Get System Data - https://localhost:5000/api/reports (GET)
- Get commands Available - https://localhost:5000/api/commands (GET)
- Add new command - https://localhost:5000/api/command (POST, json "command":"ls")
- Delete command - https://localhost:5000/api/command (DELETE, json "command":"ls")
- Get Command result - https://localhost:5000/api/command-results (GET)
