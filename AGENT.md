# Agent Instructions: MNIST Identifier System

## Project Context

Build a web application that allows user to interact (draw a 96x96 canvas), export, and make possible suggestions based on the possibility that the language model return.

## Project Architecture

### Front-end

- basic, modern UI, rounded objects (button, form,...), inspired by TailwindCSS's main page
- writing part has a gray cross to align the writing
- color palette: #212129, #323949, #3d3e51, #40445a, #4c5265
- main page:
  + canvas with 96x96
  + recommendation box
  + read-only box
  + export image into JPEG/PNG

### Back-end

- /sign-in, /sign-up (username and password only, unable to recover lost account)
- /predict (websocket endpoint)

### Language classification model

- PyTorch with GPU
- use Deep Learning to train and check if performance is better
- structure: Flatten(96, 96) 1-bit -> suitable hidden layer -> 3036 classes
- dataset: etl9g, 96x96

### Flow

1. regular work flow
   - draw when press and hold mouse
   - use websocket /predict endpoint to stream the data every draw into the language classification model
   - get top 5-15 results
   - display to the recommendation box
   - if user choose an item, append to the read-only box, renew the recommendation box, clear the canvas
2. if user want to export the image
   - parse raw bytes into black-and-white JPEG

### Tests

- use suitable testing framework for both frontend and backend
- sign-in: 3 test cases, empty, wrong, correct
- sign-up: 1 test case, check if the entered data is in db or not
- predict: 1 test case
  + check the correctness of the received data

### CI/CD

- recommend a viable option

## Tech stack

- Front-end: Next.JS + CSS
- Backend: FastAPI
- Classification model: PyTorch, Scikit-learn, NumPy, Pandas
- Database: Postgres
- Dockerize for automated CI/CD
- Write tests

## Conventions

- Separate matter of concerns
- If a function has over 40 lines, consider refactoring